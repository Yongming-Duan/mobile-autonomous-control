# APK 安装包目录

## ✅ 推荐使用

### Termux v0.79 离线版本
- **文件：** `termux-v79-offline.apk` (75 MB)
- **版本：** v0.79 (versionCode: 79)
- **说明：** 包含完整的离线 bootstrap，无需联网即可使用
- **状态：** ✅ 已成功安装并测试

### Termux:API Git 版本
- **文件：** `termux-api-git.apk` (2.2 MB)
- **版本：** Git debug
- **说明：** 与 Termux v0.79 完全兼容
- **状态：** ✅ 已成功安装

## ⚠️ 备用版本

### Termux v0.73
- **文件：** `termux-v73.apk` (206 KB)
- **说明：** 需要联网下载 bootstrap
- **状态：** 可用但不推荐（bootstrap 下载可能失败）

## ❌ 失败/不兼容

| 文件 | 大小 | 原因 |
|------|------|------|
| `termux.apk` (v118) | 13 KB | Android 5.0.2 不兼容（需要 Android 7.0+） |
| `termux-api-v29.apk` | 1.8 MB | 与 v0.79 的 sharedUserId 不匹配 |
| `termux-api.apk` (v51) | 2.8 MB | Android 5.0.2 不兼容 |
| `sensor-server.apk` | 20 MB | Android 5.0.2 不兼容 |
| 其他损坏文件 | 9 B | 下载失败 |

## 📦 安装命令

```bash
# 卸载旧版本
adb uninstall com.termux com.termux.api

# 安装推荐版本
adb install termux-v79-offline.apk
adb install termux-api-git.apk
```

## 📝 版本对比

| 版本 | Bootstrap | 大小 | 兼容性 | 推荐度 |
|------|----------|------|--------|--------|
| v0.79 离线 | ✅ 内置 | 75 MB | Android 5.0+ | ⭐⭐⭐⭐⭐ |
| v0.73 | ⚠️ 需下载 | 206 KB | Android 5.0+ | ⭐⭐⭐ |
| v118 | ❌ 在线 | 13 MB | Android 7.0+ | ⭐ |

---

**最后更新：** 2026-03-07
