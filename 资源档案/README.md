# 资源档案目录

## 💾 档案文件

### 1. Termux Legacy 仓库完整快照
**文件：** `bootstrap-archives-legacy.tar`
**大小：** 67 MB
**来源：** Internet Archive (Archive.org)
**快照日期：** 2019-12-24
**URL：** https://archive.org/details/termux-repositories-legacy

**包含内容：**
- Termux 应用（各版本）
- Termux:API（各版本）
- Bootstrap 包（所有架构）
- 完整的包仓库快照
- 源代码压缩包

**说明：**
这是 2019 年 12 月 24 日的完整 Termux 仓库快照，包含适用于 Android 5.x-6.x 的所有版本。

---

### 2. Bootstrap Archives（提取版）
**目录：** `bootstrap-archives/`
**大小：** 67 MB (解压后)
**内容：**

| 文件 | 大小 | 架构 |
|------|------|------|
| bootstrap-aarch64.zip | 17 MB | ARM 64位 |
| bootstrap-arm.zip | 17 MB | ARM 32位 |
| bootstrap-x86_64.zip | 18 MB | x86_64 |
| bootstrap-i686.zip | 17 MB | x86 32位 |
| README.txt | 92 B | 说明文件 |

**用途：**
用于离线安装 Termux bootstrap（无需联网）

---

### 3. ARM64 Bootstrap 包
**文件：** `bootstrap-arm64.zip`
**大小：** 2.1 KB
**架构：** ARM64 (aarch64)
**适用于：** 荣耀 7 (Kirin 935)

**说明：**
独立的 bootstrap 包，可以手动安装到 Termux

---

## 📊 档案统计

| 文件/目录 | 大小 | 格式 | 来源 |
|----------|------|------|------|
| bootstrap-archives-legacy.tar | 67 MB | tar | Archive.org |
| bootstrap-archives/ | 67 MB | 目录 | 提取自 tar |
| bootstrap-arm64.zip | 2.1 KB | zip | F-Droid |

**总计：** ~134 MB

---

## 🎯 使用指南

### 方法 1：使用完整快照
```bash
# 解压快照
tar -xf bootstrap-archives-legacy.tar

# 查看内容
ls bootstrap-archives/

# 选择适合的架构
# 对于荣耀 7 使用：bootstrap-aarch64.zip
```

### 方法 2：手动安装 Bootstrap
```bash
# 1. 推送到手机
adb push bootstrap-aarch64.zip /sdcard/

# 2. 在 Termux 中解压
unzip /sdcard/bootstrap-aarch64.zip -d $PREFIX/

# 3. 设置权限
chmod -R 755 $PREFIX/bin
```

### 方法 3：使用离线 APK
**推荐：** 直接使用 `termux-v79-offline.apk`
- 已内置 bootstrap
- 无需手动安装
- 开箱即用

---

## 📜 历史背景

### 为什么需要这些档案？

**问题：**
- Termux 官方已停止对 Android 5.x-6.x 的支持
- 现代版本需要 Android 7.0+
- 旧版本的在线仓库已失效

**解决方案：**
- Internet Archive 保存了 2019 年的完整快照
- 包含所有旧版本的 APK 和 bootstrap
- 可以离线安装和使用

### 版本兼容性

| Android 版本 | Termux 版本 | Bootstrap |
|-------------|-----------|----------|
| 5.0 - 5.1 | v0.73 - v0.79 | ✅ 可用 |
| 6.0 - 6.1 | v0.73 - v0.85 | ✅ 可用 |
| 7.0+ | v0.119+ | ✅ 官方支持 |

---

## 🔍 快速查找

### 荣耀 7 (Android 5.0.2) 推荐配置

**APK：** `../APK安装包/termux-v79-offline.apk`
**Bootstrap：** `bootstrap-aarch64.zip` 或使用离线 APK

---

## ⚠️ 注意事项

1. **文件完整性：**
   - 下载后请验证文件大小
   - TAR 文件应该为 67 MB
   - ZIP 文件应该为 17 MB

2. **版本选择：**
   - ARM64 设备使用 aarch64
   - ARM 32位设备使用 arm
   - x86 设备（模拟器）使用 x86_64

3. **安全提示：**
   - 仅从可信源下载（Archive.org, F-Droid）
   - 验证 APK 签名
   - 不要安装来源不明的文件

---

## 📚 相关资源

- **Archive.org Termux 页面：** https://archive.org/details/termux-repositories-legacy
- **F-Droid Termux：** https://f-droid.org/packages/com.termux/
- **Termux Wiki：** https://wiki.termux.com/

---

**最后更新：** 2026-03-07
**档案状态：** 完整保存
