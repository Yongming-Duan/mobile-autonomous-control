#!/usr/bin/env python3
"""
Autonomous Phone Agent
AI-powered autonomous agent using AutoGLM for decision making
Version: 1.0
"""

import json
import time
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import requests
import sqlite3
import os

from phone_controller import PhoneController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    SENSING = "sensing"
    THINKING = "thinking"
    ACTING = "acting"
    FEEDBACK = "feedback"
    ERROR = "error"


class ActionType(Enum):
    """Available action types"""
    TAKE_PHOTO = "take_photo"
    RECORD_AUDIO = "record_audio"
    SPEAK = "speak"
    SEND_NOTIFICATION = "send_notification"
    SEND_SMS = "send_sms"
    GET_LOCATION = "get_location"
    START_APP = "start_app"
    INPUT_TEXT = "input_text"
    TAP = "tap"
    WAIT = "wait"
    COLLECT_DATA = "collect_data"
    CUSTOM = "custom"


class AutonomousAgent:
    """
    Autonomous agent that perceives environment, makes decisions, and executes actions
    """

    def __init__(
        self,
        controller: PhoneController,
        api_key: str,
        api_base: str = "https://open.bigmodel.cn/api/paas/v4",
        model: str = "autoglm-phone",
        db_path: str = "agent_memory.db",
        autoglm_path: Optional[str] = None
    ):
        """
        Initialize autonomous agent

        Args:
            controller: PhoneController instance
            api_key: AutoGLM API key
            api_base: AutoGLM API base URL
            model: Model name
            db_path: SQLite database path for memory
            autoglm_path: Path to AutoGLM main.py (optional)
        """
        self.controller = controller
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.db_path = db_path
        self.autoglm_path = autoglm_path

        self.state = AgentState.IDLE
        self.task_queue: List[Dict] = []
        self.running = False
        self.cycle_count = 0

        # Initialize database
        self._init_database()

        logger.info("AutonomousAgent initialized")

    def _init_database(self):
        """Initialize SQLite database for memory"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()

        # Perceptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS perceptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                data JSON,
                summary TEXT
            )
        ''')

        # Decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                perception_id INTEGER,
                action_type TEXT,
                action_params JSON,
                reasoning TEXT
            )
        ''')

        # Actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                decision_id INTEGER,
                action_type TEXT,
                status TEXT,
                result JSON,
                feedback TEXT
            )
        ''')

        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                task TEXT,
                status TEXT,
                priority INTEGER DEFAULT 0
            )
        ''')

        self.conn.commit()
        logger.info(f"Database initialized: {self.db_path}")

    # ==================== PERCEPTION ====================

    def perceive_environment(self) -> Dict[str, Any]:
        """
        Collect complete environment snapshot

        Returns:
            Environment data
        """
        logger.info("Perceiving environment...")
        self.state = AgentState.SENSING

        try:
            env_data = self.controller.get_environment_snapshot()

            # Store perception
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO perceptions (data, summary) VALUES (?, ?)',
                (json.dumps(env_data), self._summarize_env(env_data))
            )
            self.conn.commit()

            self.state = AgentState.IDLE
            return env_data

        except Exception as e:
            logger.error(f"Perception failed: {e}")
            self.state = AgentState.ERROR
            return {}

    def _summarize_env(self, env_data: Dict) -> str:
        """Create human-readable summary of environment"""
        summary_parts = []

        # Battery
        battery = env_data.get("battery", {})
        if battery:
            summary_parts.append(f"Battery: {battery.get('percentage')}%")

        # Location
        location = env_data.get("location")
        if location:
            summary_parts.append(f"Location: {location.get('latitude'):.4f}, {location.get('longitude'):.4f}")

        # Light
        light = env_data.get("sensors", {}).get("light")
        if light:
            summary_parts.append(f"Light: {light} lux")

        # WiFi
        wifi = env_data.get("wifi")
        if wifi:
            summary_parts.append(f"WiFi: {wifi.get('ssid')}")

        return ". ".join(summary_parts) if summary_parts else "No data"

    # ==================== DECISION MAKING ====================

    def make_decision(
        self,
        env_data: Dict[str, Any],
        task: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make decision based on environment and task

        Args:
            env_data: Environment snapshot
            task: Optional task description
            context: Additional context

        Returns:
            Decision dict with action_type and action_params
        """
        logger.info("Making decision...")
        self.state = AgentState.THINKING

        try:
            # Build prompt
            prompt = self._build_decision_prompt(env_data, task, context)

            # Call AutoGLM API
            decision = self._call_autoglm(prompt)

            # Parse decision
            parsed_decision = self._parse_decision(decision)

            # Store decision
            cursor = self.conn.cursor()
            cursor.execute(
                '''INSERT INTO decisions
                   (perception_id, action_type, action_params, reasoning)
                   VALUES (
                     (SELECT id FROM perceptions ORDER BY id DESC LIMIT 1),
                     ?, ?, ?
                   )''',
                (
                    parsed_decision.get("action_type"),
                    json.dumps(parsed_decision.get("action_params")),
                    parsed_decision.get("reasoning", "")
                )
            )
            self.conn.commit()

            self.state = AgentState.IDLE
            return parsed_decision

        except Exception as e:
            logger.error(f"Decision making failed: {e}")
            self.state = AgentState.ERROR

            # Fallback: safe default action
            return {
                "action_type": ActionType.WAIT.value,
                "action_params": {"duration": 10},
                "reasoning": f"Error in decision: {e}"
            }

    def _build_decision_prompt(
        self,
        env_data: Dict,
        task: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """Build prompt for AutoGLM"""

        prompt_parts = [
            "You are an autonomous phone agent. Based on the current environment state,",
            "decide what action to take next.\n"
        ]

        # Add task if provided
        if task:
            prompt_parts.append(f"CURRENT TASK: {task}\n")

        # Add environment data
        prompt_parts.append("CURRENT ENVIRONMENT:")
        prompt_parts.append(json.dumps(env_data, indent=2, ensure_ascii=False))
        prompt_parts.append("")

        # Add available actions
        prompt_parts.append("AVAILABLE ACTIONS:")
        for action in ActionType:
            prompt_parts.append(f"  - {action.value}")

        prompt_parts.append("")
        prompt_parts.append(
            "Respond with JSON in this format:\n"
            '{\n'
            '  "action_type": "action_name",\n'
            '  "action_params": {"param": "value"},\n'
            '  "reasoning": "why this action"\n'
            '}\n'
            "Choose the most appropriate action based on the environment and task."
        )

        return "\n".join(prompt_parts)

    def _call_autoglm(self, prompt: str) -> str:
        """Call AutoGLM API"""

        # Try API first
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )

            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.warning(f"AutoGLM API call failed: {e}")

            # Fallback to AutoGLM command line
            if self.autoglm_path:
                return self._call_autoglm_cli(prompt)
            else:
                raise

    def _call_autoglm_cli(self, prompt: str) -> str:
        """Call AutoGLM via command line"""
        try:
            result = subprocess.run(
                [
                    "python", self.autoglm_path,
                    "--base-url", self.api_base,
                    "--model", self.model,
                    "--apikey", self.api_key,
                    prompt
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return result.stdout
            else:
                raise Exception(f"AutoGLM CLI failed: {result.stderr}")

        except Exception as e:
            logger.error(f"AutoGLM CLI failed: {e}")
            raise

    def _parse_decision(self, decision_text: str) -> Dict[str, Any]:
        """Parse decision from AutoGLM response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^{}]*"action_type"[^{}]*\}', decision_text, re.DOTALL)

            if json_match:
                decision = json.loads(json_match.group(0))

                # Validate action_type
                try:
                    action_type = ActionType(decision.get("action_type"))
                    decision["action_type"] = action_type.value
                except ValueError:
                    logger.warning(f"Unknown action type: {decision.get('action_type')}")
                    decision["action_type"] = ActionType.WAIT.value

                return decision

            else:
                # Fallback: try to extract action type from text
                for action in ActionType:
                    if action.value in decision_text.lower():
                        return {
                            "action_type": action.value,
                            "action_params": {},
                            "reasoning": decision_text
                        }

                # Default fallback
                return {
                    "action_type": ActionType.WAIT.value,
                    "action_params": {"duration": 10},
                    "reasoning": f"Could not parse decision: {decision_text}"
                }

        except Exception as e:
            logger.error(f"Failed to parse decision: {e}")
            return {
                "action_type": ActionType.WAIT.value,
                "action_params": {"duration": 10},
                "reasoning": f"Parse error: {e}"
            }

    # ==================== ACTION EXECUTION ====================

    def execute_action(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action based on decision

        Args:
            decision: Decision dict from make_decision()

        Returns:
            Action result
        """
        logger.info(f"Executing action: {decision.get('action_type')}")
        self.state = AgentState.ACTING

        try:
            action_type = decision.get("action_type")
            action_params = decision.get("action_params", {})

            result = self._perform_action(action_type, action_params)

            # Store action
            cursor = self.conn.cursor()
            cursor.execute(
                '''INSERT INTO actions (decision_id, action_type, status, result, feedback)
                   VALUES (
                     (SELECT id FROM decisions ORDER BY id DESC LIMIT 1),
                     ?, ?, ?, ?
                   )''',
                (
                    action_type,
                    "success" if result.get("success") else "failed",
                    json.dumps(result),
                    result.get("feedback", "")
                )
            )
            self.conn.commit()

            self.state = AgentState.IDLE
            return result

        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            self.state = AgentState.ERROR

            return {
                "success": False,
                "error": str(e),
                "feedback": f"Execution error: {e}"
            }

    def _perform_action(self, action_type: str, params: Dict) -> Dict[str, Any]:
        """Perform specific action"""

        try:
            if action_type == ActionType.TAKE_PHOTO.value:
                return self._action_take_photo(params)

            elif action_type == ActionType.RECORD_AUDIO.value:
                return self._action_record_audio(params)

            elif action_type == ActionType.SPEAK.value:
                return self._action_speak(params)

            elif action_type == ActionType.SEND_NOTIFICATION.value:
                return self._action_send_notification(params)

            elif action_type == ActionType.SEND_SMS.value:
                return self._action_send_sms(params)

            elif action_type == ActionType.GET_LOCATION.value:
                return self._action_get_location(params)

            elif action_type == ActionType.START_APP.value:
                return self._action_start_app(params)

            elif action_type == ActionType.INPUT_TEXT.value:
                return self._action_input_text(params)

            elif action_type == ActionType.TAP.value:
                return self._action_tap(params)

            elif action_type == ActionType.WAIT.value:
                return self._action_wait(params)

            elif action_type == ActionType.COLLECT_DATA.value:
                return self._action_collect_data(params)

            elif action_type == ActionType.CUSTOM.value:
                return self._action_custom(params)

            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action_type}",
                    "feedback": "Action not implemented"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "feedback": f"Action error: {e}"
            }

    # Individual action implementations

    def _action_take_photo(self, params: Dict) -> Dict:
        """Take photo action"""
        camera_id = params.get("camera_id", "0")
        result = self.controller.take_photo(camera_id)

        if result.get("status") == "success":
            return {
                "success": True,
                "feedback": f"Photo saved: {result.get('filename')}",
                "data": result
            }
        else:
            return {
                "success": False,
                "error": result.get("message"),
                "feedback": "Failed to take photo"
            }

    def _action_record_audio(self, params: Dict) -> Dict:
        """Record audio action"""
        duration = params.get("duration", 5)
        result = self.controller.record_audio(duration)

        if result.get("status") == "success":
            return {
                "success": True,
                "feedback": f"Audio recorded: {result.get('filename')}",
                "data": result
            }
        else:
            return {
                "success": False,
                "error": result.get("message"),
                "feedback": "Failed to record audio"
            }

    def _action_speak(self, params: Dict) -> Dict:
        """Speak action"""
        text = params.get("text", "Task completed")
        rate = params.get("rate", 1.0)
        pitch = params.get("pitch", 1.0)

        success = self.controller.speak(text, rate, pitch)

        return {
            "success": success,
            "feedback": f"Spoke: {text}" if success else "Failed to speak"
        }

    def _action_send_notification(self, params: Dict) -> Dict:
        """Send notification action"""
        title = params.get("title", "Notification")
        content = params.get("content", "")
        notification_id = params.get("id", "1")

        success = self.controller.send_notification(title, content, notification_id)

        return {
            "success": success,
            "feedback": "Notification sent" if success else "Failed to send notification"
        }

    def _action_send_sms(self, params: Dict) -> Dict:
        """Send SMS action"""
        number = params.get("number")
        text = params.get("text", "")

        if not number:
            return {
                "success": False,
                "error": "Phone number required",
                "feedback": "Missing parameter: number"
            }

        success = self.controller.send_sms(number, text)

        return {
            "success": success,
            "feedback": f"SMS sent to {number}" if success else "Failed to send SMS"
        }

    def _action_get_location(self, params: Dict) -> Dict:
        """Get location action"""
        use_last = params.get("use_last", True)
        location = self.controller.get_location(use_last)

        if location:
            return {
                "success": True,
                "feedback": f"Location: {location.get('latitude')}, {location.get('longitude')}",
                "data": location
            }
        else:
            return {
                "success": False,
                "error": "Failed to get location",
                "feedback": "Location unavailable"
            }

    def _action_start_app(self, params: Dict) -> Dict:
        """Start app action"""
        package = params.get("package")

        if not package:
            return {
                "success": False,
                "error": "Package name required",
                "feedback": "Missing parameter: package"
            }

        success = self.controller.start_app(package)

        return {
            "success": success,
            "feedback": f"Started: {package}" if success else f"Failed to start: {package}"
        }

    def _action_input_text(self, params: Dict) -> Dict:
        """Input text action"""
        text = params.get("text", "")

        success = self.controller.input_text(text)

        return {
            "success": success,
            "feedback": f"Input: {text}" if success else "Failed to input text"
        }

    def _action_tap(self, params: Dict) -> Dict:
        """Tap action"""
        x = params.get("x")
        y = params.get("y")

        if x is None or y is None:
            return {
                "success": False,
                "error": "Coordinates required",
                "feedback": "Missing parameters: x, y"
            }

        success = self.controller.tap(int(x), int(y))

        return {
            "success": success,
            "feedback": f"Tapped: ({x}, {y})" if success else "Failed to tap"
        }

    def _action_wait(self, params: Dict) -> Dict:
        """Wait action"""
        duration = params.get("duration", 10)
        time.sleep(duration)

        return {
            "success": True,
            "feedback": f"Waited {duration} seconds"
        }

    def _action_collect_data(self, params: Dict) -> Dict:
        """Collect data action"""
        sensors = params.get("sensors", ["accelerometer", "light", "battery"])
        duration = params.get("duration", 60)
        interval = params.get("interval", 1)

        # Simple data collection
        collected = {}
        for sensor in sensors:
            if sensor == "battery":
                collected[sensor] = self.controller.get_battery()
            else:
                collected[sensor] = self.controller.get_sensor_data(sensor, 1)

        return {
            "success": True,
            "feedback": f"Collected data from {len(sensors)} sensors",
            "data": collected
        }

    def _action_custom(self, params: Dict) -> Dict:
        """Custom action - can be extended"""
        command = params.get("command")

        if command == "print_status":
            self.controller.print_status()
            return {
                "success": True,
                "feedback": "Status printed"
            }

        return {
            "success": False,
            "error": "Unknown custom command",
            "feedback": f"Unknown command: {command}"
        }

    # ==================== MAIN LOOP ====================

    def run_autonomous_cycle(
        self,
        task: Optional[str] = None,
        cycles: int = 1,
        cycle_delay: int = 5
    ):
        """
        Run autonomous sense-think-act cycle

        Args:
            task: Optional task description
            cycles: Number of cycles to run (0 = infinite)
            cycle_delay: Delay between cycles in seconds
        """
        logger.info("Starting autonomous cycle...")
        self.running = True
        self.cycle_count = 0

        try:
            while self.running and (cycles == 0 or self.cycle_count < cycles):
                self.cycle_count += 1
                logger.info(f"\n=== Cycle {self.cycle_count} ===")

                # 1. Perceive
                env_data = self.perceive_environment()

                # 2. Think
                decision = self.make_decision(env_data, task)

                # 3. Act
                result = self.execute_action(decision)

                # 4. Feedback
                logger.info(f"Cycle result: {result.get('feedback')}")

                # Wait before next cycle
                if cycle_delay > 0:
                    logger.info(f"Waiting {cycle_delay} seconds...")
                    time.sleep(cycle_delay)

        except KeyboardInterrupt:
            logger.info("\nCycle interrupted by user")
        finally:
            self.running = False
            logger.info(f"Autonomous cycle ended. Total cycles: {self.cycle_count}")

    def stop(self):
        """Stop autonomous cycle"""
        self.running = False
        logger.info("Stopping agent...")

    # ==================== TASK MANAGEMENT ====================

    def add_task(self, task: str, priority: int = 0):
        """
        Add task to queue

        Args:
            task: Task description
            priority: Task priority (higher = more important)
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO tasks (task, status, priority) VALUES (?, ?, ?)',
            (task, 'pending', priority)
        )
        self.conn.commit()
        logger.info(f"Task added: {task}")

    def get_next_task(self) -> Optional[Dict]:
        """Get highest priority pending task"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM tasks WHERE status = "pending" ORDER BY priority DESC, id ASC LIMIT 1'
        )
        row = cursor.fetchone()

        if row:
            return {
                "id": row[0],
                "task": row[2],
                "priority": row[4]
            }
        return None

    def complete_task(self, task_id: int):
        """Mark task as completed"""
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE tasks SET status = "completed" WHERE id = ?',
            (task_id,)
        )
        self.conn.commit()

    # ==================== REPORTING ====================

    def generate_report(self, cycles: int = 10) -> Dict:
        """
        Generate activity report

        Args:
            cycles: Number of recent cycles to include

        Returns:
            Report dictionary
        """
        cursor = self.conn.cursor()

        # Get recent perceptions
        cursor.execute('SELECT * FROM perceptions ORDER BY id DESC LIMIT ?', (cycles,))
        perceptions = cursor.fetchall()

        # Get recent decisions
        cursor.execute('SELECT * FROM decisions ORDER BY id DESC LIMIT ?', (cycles,))
        decisions = cursor.fetchall()

        # Get recent actions
        cursor.execute('SELECT * FROM actions ORDER BY id DESC LIMIT ?', (cycles,))
        actions = cursor.fetchall()

        # Get pending tasks
        cursor.execute('SELECT * FROM tasks WHERE status = "pending"')
        pending_tasks = cursor.fetchall()

        return {
            "timestamp": datetime.now().isoformat(),
            "cycle_count": self.cycle_count,
            "state": self.state.value,
            "recent_cycles": cycles,
            "perception_count": len(perceptions),
            "decision_count": len(decisions),
            "action_count": len(actions),
            "pending_tasks": len(pending_tasks),
            "recent_perceptions": perceptions[:5],
            "recent_decisions": decisions[:5],
            "recent_actions": actions[:5]
        }


# ==================== PRESET BEHAVIORS ====================

class SurveillanceAgent(AutonomousAgent):
    """
    Autonomous surveillance agent
    Monitors environment and records suspicious activity
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseline_light = None
        self.baseline_noise = None
        self.calibration_cycles = 5

    def run_surveillance_cycle(self):
        """Run surveillance-specific cycle"""

        # Calibrate baseline
        if self.cycle_count < self.calibration_cycles:
            logger.info("Calibrating baseline...")
            env_data = self.perceive_environment()

            light = env_data.get("sensors", {}).get("light")
            if light:
                self.baseline_light = light

            logger.info(f"Baseline light: {self.baseline_light}")

        # Normal surveillance cycle
        env_data = self.perceive_environment()

        # Check for anomalies
        current_light = env_data.get("sensors", {}).get("light")

        if self.baseline_light and current_light:
            light_change = abs(current_light - self.baseline_light)

            # Significant light change detected
            if light_change > 50:
                logger.warning(f"Light anomaly detected: {light_change} lux change")

                # Take photo
                decision = {
                    "action_type": ActionType.TAKE_PHOTO.value,
                    "action_params": {"camera_id": "0"},
                    "reasoning": f"Light anomaly: {light_change} lux"
                }

                result = self.execute_action(decision)

                # Alert user
                self.controller.speak("Suspicious activity detected")

                # Send notification
                self.controller.send_notification(
                    "Security Alert",
                    f"Light anomaly detected: {light_change} lux change at {datetime.now().strftime('%H:%M')}"
                )

        # Wait and continue
        time.sleep(30)


class EnvironmentMonitorAgent(AutonomousAgent):
    """
    Environment monitoring agent
    Tracks environmental conditions and reports
    """

    def run_monitoring_cycle(self):
        """Run environment monitoring cycle"""

        # Collect data
        env_data = self.perceive_environment()

        # Check battery
        battery = env_data.get("battery", {})
        if battery:
            percentage = battery.get("percentage")

            if percentage and percentage < 20:
                # Low battery warning
                self.controller.speak(f"Low battery: {percentage}% remaining")

        # Log conditions
        logger.info(f"Environment: Light={env_data.get('sensors', {}).get('light')} lux, "
                   f"Temp={battery.get('temperature', 0)/10 if battery else 0}°C, "
                   f"Battery={battery.get('percentage', 0) if battery else 0}%")


# ==================== MAIN / EXAMPLES ====================

if __name__ == "__main__":
    import sys

    # Example usage
    API_KEY = "YOUR_AUTOGLM_API_KEY"  # Replace with your API key

    # Create controller
    controller = PhoneController()

    # Create agent
    agent = AutonomousAgent(
        controller=controller,
        api_key=API_KEY,
        model="autoglm-phone"
    )

    # Run autonomous cycle with task
    try:
        agent.run_autonomous_cycle(
            task="Monitor the environment and report any changes",
            cycles=5,
            cycle_delay=10
        )
    except KeyboardInterrupt:
        agent.stop()

    # Generate report
    report = agent.generate_report()
    print("\n=== AGENT REPORT ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
