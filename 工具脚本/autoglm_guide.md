# AutoGLM 自动化控制使用指南

## 📋 配置信息

| 项目 | 值 |
|------|------|
| API地址 | https://open.bigmodel.cn/api/paas/v4 |
| 模型 | autoglm-phone |
| API密钥 | 1b3d58e728f84e38b8872bf09e3217f8.UTF48shlSo4dYykv |

## 🚀 使用前准备

### 第一步：确保ADB连接

在手机上：
```
1. 插入USB线
2. 允许USB调试（勾选"始终允许"）
3. 保持屏幕唤醒
```

验证连接：
```batch
cd 工具软件/platform-tools
.\adb.exe devices
```

### 第二步：确保Python环境

AutoGLM需要Python环境，已安装在：
```
工具软件/Open-AutoGLM/
```

依赖包：
- Pillow (图像处理)
- openai (API客户端)
- requests (HTTP请求)

## 📱 AutoGLM命令示例

### 基础命令格式
```batch
cd 工具脚本
.\autoglm.bat "任务描述"
```

### 实用示例

#### 1. 打开设置查看设备信息
```batch
.\autoglm.bat "打开设置查看设备信息"
```

#### 2. 启动相机拍照
```batch
.\autoglm.bat "打开相机拍照"
```

#### 3. 测试麦克风
```batch
.\autoglm.bat "打开录音应用"
```

#### 4. 打开微信
```batch
.\autoglm.bat "打开微信"
```

#### 5. 搜索功能
```batch
.\autoglm.bat "打开浏览器搜索荣耀7刷机教程"
```

#### 6. 应用操作
```batch
.\autoglm.bat "打开设置中的WiFi设置"
```

#### 7. 文件管理
```batch
.\autoglm.bat "打开文件管理查看下载文件夹"
```

## 🎯 交互模式

进入交互模式可以连续执行多个任务：

```batch
cd 工具脚本
.\autoglm.bat interactive
```

然后输入任务描述，AutoGLM会持续运行直到您退出。

## ⚠️ 常见问题

### 问题1：ADB未连接
**解决方案：**
```batch
# 重启ADB
cd 工具软件/platform-tools
.\adb.exe kill-server
.\adb.exe start-server
.\adb.exe devices
```

### 问题2：API密钥无效
**解决方案：**
- 访问 https://bigmodel.cn/
- 注册并获取新的API密钥
- 更新 autoglm.bat 第18行

### 问题3：Python环境问题
**解决方案：**
```batch
cd 工具软件/Open-AutoGLM
pip install -r requirements.txt
```

### 问题4：屏幕识别失败
**解决方案：**
- 确保手机屏幕完全唤醒
- 调整屏幕亮度到适中
- 确保没有弹窗遮挡

## 📊 性能指标

根据测试报告，AutoGLM性能：

| 指标 | 数值 |
|------|------|
| 首Token延迟 | 1.3-2.7秒 |
| 思考完成延迟 | 1.9-5.3秒 |
| 总推理时间 | 2.1-5.5秒 |

## 💡 高级用法

### 1. 批量任务

创建任务文件 tasks.txt：
```
打开设置查看设备信息
打开相机拍照
打开录音应用
```

然后逐个执行：
```batch
for /f "tokens=*" %a in (tasks.txt) do .\autoglm.bat "%a"
```

### 2. 定时任务

使用Windows任务计划程序定时执行AutoGLM命令。

### 3. 日志记录

```batch
.\autoglm.bat "任务描述" > autoglm_log.txt 2>&1
```

## 🔧 故障排除

### AutoGLM无法控制手机

**检查项：**
1. ADB连接是否正常
2. USB调试是否开启
3. 屏幕是否唤醒
4. API密钥是否有效

### AutoGLM执行缓慢

**优化方法：**
1. 检查网络连接
2. 减少任务复杂度
3. 分解复杂任务为多个简单任务

## 📚 相关资源

- **AutoGLM GitHub:** https://github.com/zai-org/Open-AutoGLM
- **智谱 BigModel:** https://bigmodel.cn/
- **项目测试报告:** 测试报告/AutoGLM_Termux_测试报告.md

---

**最后更新：** 2026-03-08
**维护者：** Claude Code
