# Contributing to Mobile Autonomous Control System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Android 5.0+ device
- Python 3.8+
- ADB tools
- Termux on Android device
- Termux:API installed

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mobile-autonomous-control.git
cd mobile-autonomous-control
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Deploy sensor server to your Android device:
```bash
adb push 工具脚本/enhanced_sensor_server.py /sdcard/
```

4. Start the sensor server in Termux:
```bash
cd /sdcard
python enhanced_sensor_server.py
```

5. Run the startup script:
```bash
python 工具脚本/go.py
```

## Code Style

- Follow PEP 8 guidelines
- Use 4 spaces for indentation
- Maximum line length: 127 characters
- Add docstrings to all functions and classes

### Example

```python
def get_sensor_data(self, sensor_type, limit=1):
    """
    Read sensor data from the device.

    Args:
        sensor_type (str): Type of sensor to read
        limit (int): Number of readings to retrieve

    Returns:
        dict: JSON response from the API
    """
    return self._api_request("GET", f"/sensor/{sensor_type}",
                            params={"limit": limit})
```

## Testing

Before submitting a pull request:

1. Test on actual Android device
2. Verify all API endpoints work
3. Check dashboard displays data correctly
4. Test data collection and storage

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

### Commit Message Format

Use conventional commit messages:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test updates
- `chore:` - Build or maintenance tasks

Example:
```
feat: add gyroscope data recording to autonomous agent

- Implement gyroscope data collection
- Add rotation detection logic
- Update dashboard to show rotation data
```

## Project Structure

```
mobile-autonomous-control/
├── 工具脚本/           # Core implementation
│   ├── enhanced_sensor_server.py    # Termux HTTP server
│   ├── phone_controller.py          # Python control library
│   ├── autonomous_agent.py          # AI autonomous agent
│   ├── data_collector.py            # Data collection system
│   ├── dashboard.py                 # Flask web dashboard
│   └── templates/
│       └── dashboard.html           # Dashboard frontend
├── 工具软件/           # External tools
├── .github/
│   └── workflows/                   # CI/CD workflows
├── docs/                            # Documentation
├── requirements.txt                 # Python dependencies
└── README_GITHUB.md                 # Project README
```

## Reporting Issues

When reporting bugs, please include:

1. Device model and Android version
2. Python version
3. Error messages or stack traces
4. Steps to reproduce the issue
5. Expected vs actual behavior

## Feature Requests

We welcome feature requests! Please:

1. Check if the feature already exists
2. Search existing issues first
3. Describe the use case clearly
4. Provide examples of how you'd use it

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue for questions or discussions.
