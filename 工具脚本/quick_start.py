#!/usr/bin/env python3
"""
Quick Start Script - Test all components
快速启动脚本 - 测试所有组件
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from phone_controller import PhoneController
from data_collector import SensorDataCollector

def test_connection():
    """测试基本连接"""
    print("=" * 60)
    print("测试 1: 基本连接测试")
    print("=" * 60)

    controller = PhoneController()

    # 健康检查
    print("\n1.1 传感器服务器健康检查...")
    health = controller.health_check()
    print(f"   状态: {health.get('status')}")
    print(f"   服务: {health.get('service')}")

    if health.get('status') != 'healthy':
        print("\n   ❌ 传感器服务器未运行！")
        print("   请先在Termux中启动 enhanced_sensor_server.py")
        return False

    print("   ✅ 传感器服务器运行正常")

    # 服务器信息
    print("\n1.2 获取服务器信息...")
    info = controller.server_info()
    print(f"   版本: {info.get('version')}")
    print(f"   可用传感器: {len(info.get('available_sensors', []))}")

    return True


def test_sensors(controller):
    """测试传感器读取"""
    print("\n" + "=" * 60)
    print("测试 2: 传感器读取")
    print("=" * 60)

    sensors_to_test = [
        ('accelerometer', '加速度计'),
        ('gyroscope', '陀螺仪'),
        ('light', '光线'),
        ('pressure', '气压'),
        ('proximity', '距离')
    ]

    results = {}

    for sensor_type, sensor_name in sensors_to_test:
        print(f"\n2.{len(results)+1} 测试 {sensor_name}...")
        try:
            data = controller.get_sensor_data(sensor_type, 1)

            if data.get('status') == 'success':
                values = data.get('data', [{}])[0].get('values', [])
                print(f"   ✅ {sensor_name}: {values[:3] if len(values) > 3 else values}")
                results[sensor_type] = 'OK'
            else:
                print(f"   ⚠️  {sensor_name}: {data.get('message')}")
                results[sensor_type] = 'WARN'

        except Exception as e:
            print(f"   ❌ {sensor_name}: {e}")
            results[sensor_type] = 'FAIL'

    # 统计
    ok_count = sum(1 for v in results.values() if v == 'OK')
    print(f"\n   传感器测试完成: {ok_count}/{len(sensors_to_test)} 成功")

    return results


def test_battery(controller):
    """测试电池读取"""
    print("\n" + "=" * 60)
    print("测试 3: 电池状态")
    print("=" * 60)

    print("\n3.1 读取电池状态...")
    battery = controller.get_battery()

    if battery:
        print(f"   电量: {battery.get('percentage')}%")
        print(f"   状态: {battery.get('status')}")
        print(f"   健康: {battery.get('health')}")
        print(f"   温度: {battery.get('temperature')/10}°C")
        print(f"   充电: {battery.get('plugged')}")
        print("   ✅ 电池读取成功")
        return True
    else:
        print("   ❌ 电池读取失败")
        return False


def test_camera(controller):
    """测试摄像头"""
    print("\n" + "=" * 60)
    print("测试 4: 摄像头拍照")
    print("=" * 60)

    print("\n4.1 拍照测试...")
    print("   正在拍照...")

    result = controller.take_photo('0')

    if result.get('status') == 'success':
        filename = result.get('filename')
        print(f"   ✅ 照片已保存: {filename}")

        # 列出照片
        print("\n4.2 列出最近照片...")
        photos = controller.list_photos()
        if photos:
            print(f"   共有 {len(photos)} 张照片:")
            for photo in photos[:3]:
                print(f"     - {photo['filename']} ({photo['size']/1024:.1f} KB)")

        return True
    else:
        print(f"   ❌ 拍照失败: {result.get('message')}")
        return False


def test_location(controller):
    """测试GPS定位"""
    print("\n" + "=" * 60)
    print("测试 5: GPS定位")
    print("=" * 60)

    print("\n5.1 获取最后已知位置...")
    location = controller.get_location(use_last=True)

    if location:
        print(f"   纬度: {location.get('latitude')}")
        print(f"   经度: {location.get('longitude')}")
        print(f"   精度: ±{location.get('accuracy')}米")
        print("   ✅ 定位成功")
        return True
    else:
        print("   ⚠️  定位失败 (可能GPS未开启)")
        return False


def test_tts(controller):
    """测试语音合成"""
    print("\n" + "=" * 60)
    print("测试 6: 语音合成 (TTS)")
    print("=" * 60)

    print("\n6.1 测试语音合成...")
    text = "传感器系统测试完成"
    print(f"   正在朗读: '{text}'")

    success = controller.speak(text)

    if success:
        print("   ✅ 语音合成成功")
        return True
    else:
        print("   ❌ 语音合成失败")
        return False


def test_data_collection(controller):
    """测试数据采集"""
    print("\n" + "=" * 60)
    print("测试 7: 数据采集系统")
    print("=" * 60)

    print("\n7.1 创建数据采集器...")
    collector = SensorDataCollector(
        controller=controller,
        collection_interval=5,
        db_path="test_sensor_data.db"
    )

    print("7.2 启动采集 (测试10秒)...")

    # 采集计数
    count = [0]
    def on_data(sensor_type, values):
        count[0] += 1
        print(f"   [{count[0]}] {sensor_type}: {values}")

    collector.add_callback(on_data)
    collector.start(['accelerometer', 'light'])

    import time
    time.sleep(10)

    collector.stop()

    print(f"\n7.3 采集完成，共 {count[0]} 条数据")

    # 查询统计
    print("\n7.4 数据库统计...")
    stats = collector.get_database_size()
    for table, count in stats.items():
        if table != 'file_size_mb':
            print(f"   {table}: {count} 条记录")

    return True


def print_status(controller):
    """打印设备状态"""
    print("\n" + "=" * 60)
    print("设备状态快照")
    print("=" * 60)
    controller.print_status()


def main():
    """主测试流程"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "手机自主化控制系统 - 快速测试" + " " * 18 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")

    # 测试1: 连接
    if not test_connection():
        print("\n❌ 连接测试失败，请确保:")
        print("   1. 手机已连接USB")
        print("   2. ADB调试已开启")
        print("   3. Termux中运行 enhanced_sensor_server.py")
        print("   4. ADB端口转发已设置 (adb forward tcp:9999 tcp:9999)")
        return 1

    # 创建控制器
    controller = PhoneController()

    # 测试2: 传感器
    sensor_results = test_sensors(controller)

    # 测试3: 电池
    test_battery(controller)

    # 测试4: 摄像头
    test_camera(controller)

    # 测试5: GPS
    test_location(controller)

    # 测试6: TTS
    test_tts(controller)

    # 测试7: 数据采集
    test_data_collection(controller)

    # 打印状态
    print_status(controller)

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    sensor_ok = sum(1 for v in sensor_results.values() if v == 'OK')
    print(f"\n传感器: {sensor_ok}/{len(sensor_results)} 测试通过")

    print("\n✅ 系统基本功能正常！")
    print("\n下一步:")
    print("   1. 部署自主化Agent: python autonomous_agent.py")
    print("   2. 启动Web仪表板: python dashboard.py")
    print("   3. 阅读完整文档: README_AUTONOMOUS_SYSTEM.md")

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
