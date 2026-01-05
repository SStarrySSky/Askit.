"""
PAskit MSI/EXE 安装器制作指南

本指南说明如何为PAskit创建Windows安装程序。
"""

# ============================================================================
# 方案1：使用NSIS创建EXE安装程序（推荐）
# ============================================================================

## 什么是NSIS？

NSIS（Nullsoft Scriptable Install System）是一个轻量级的Windows安装程序生成工具。
- 文件小（~1-2MB）
- 功能完整
- 易于定制
- 广泛使用

## 安装NSIS

### 方法1：直接下载安装
1. 访问：https://nsis.sourceforge.io/
2. 下载最新版本
3. 运行安装程序
4. 默认安装到 C:\Program Files (x86)\NSIS

### 方法2：使用Chocolatey（推荐）
```bash
choco install nsis
```

### 方法3：使用Winget
```bash
winget install NSIS.NSIS
```

## 生成安装程序

### 步骤1：确保已生成可执行文件
```bash
python build.py
```

### 步骤2：运行安装程序生成脚本
```bash
python create_installer.py
```

### 步骤3：等待编译完成
脚本会自动：
- 检查NSIS是否安装
- 编译installer.nsi脚本
- 生成PAskit-installer.exe

### 输出文件
```
release/
└── PAskit-installer.exe  # Windows安装程序
```

## 安装程序功能

✓ 安装到Program Files
✓ 创建开始菜单快捷方式
✓ 创建桌面快捷方式
✓ 包含卸载程序
✓ 注册表集成
✓ 支持静默安装

## 用户安装步骤

1. **下载** - 用户下载 PAskit-installer.exe
2. **运行** - 双击安装程序
3. **选择安装位置** - 默认为 C:\Program Files\PAskit
4. **完成安装** - 点击完成
5. **启动应用** - 从开始菜单或桌面快捷方式启动

## 静默安装（企业部署）

管理员可以使用以下命令进行静默安装：

```bash
# 静默安装到默认位置
PAskit-installer.exe /S

# 静默安装到自定义位置
PAskit-installer.exe /S /D=C:\CustomPath\PAskit

# 静默卸载
PAskit-installer.exe /S /un
```

---

# ============================================================================
# 方案2：使用ZIP分发（无需NSIS）
# ============================================================================

如果不想安装NSIS，可以直接分发ZIP文件：

```bash
# 已自动生成
release/PAskit-release.zip
```

用户只需：
1. 下载 PAskit-release.zip
2. 解压到任意位置
3. 运行 PAskit.exe

---

# ============================================================================
# 自定义安装程序
# ============================================================================

## 修改安装程序外观

编辑 installer.nsi 文件：

```nsi
; 修改应用名称
Name "PAskit 1.0"

; 修改安装目录
InstallDir "$PROGRAMFILES\MyApp"

; 修改输出文件名
OutFile "MyApp-setup.exe"
```

## 添加许可证页面

在 installer.nsi 中添加：

```nsi
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
```

## 添加自定义页面

```nsi
!insertmacro MUI_PAGE_COMPONENTS
```

---

# ============================================================================
# 故障排除
# ============================================================================

### 问题1：找不到NSIS
**解决方案**：
- 确保NSIS已安装
- 检查安装路径是否为标准位置
- 手动指定NSIS路径

### 问题2：编译失败
**解决方案**：
- 检查installer.nsi文件是否存在
- 确保PAskit.exe已生成
- 查看错误日志

### 问题3：安装程序太大
**解决方案**：
- 这是正常的（包含所有依赖）
- 可以使用UPX压缩
- 或使用ZIP分发

---

# ============================================================================
# 发布清单
# ============================================================================

发布前检查：

- [ ] 运行 python build.py 生成可执行文件
- [ ] 运行 python create_installer.py 生成安装程序
- [ ] 测试安装程序
- [ ] 测试卸载程序
- [ ] 验证快捷方式
- [ ] 验证激活功能
- [ ] 检查文件大小
- [ ] 准备发布说明

---

# ============================================================================
# 快速命令参考
# ============================================================================

```bash
# 1. 生成可执行文件
python build.py

# 2. 生成安装程序
python create_installer.py

# 3. 生成激活码
python generate_activation_code.py

# 4. 测试安装程序
release/PAskit-installer.exe

# 5. 静默安装（测试）
release/PAskit-installer.exe /S /D=C:\Test\PAskit
```

---

# ============================================================================
# 总结
# ============================================================================

### 完整发布流程

```
1. python build.py              # 生成可执行文件
   ↓
2. python create_installer.py   # 生成安装程序
   ↓
3. 测试 release/PAskit-installer.exe
   ↓
4. 分发 release/PAskit-installer.exe 给用户
```

### 文件大小参考

| 文件 | 大小 |
|------|------|
| PAskit.exe | 150-200MB |
| PAskit-installer.exe | 160-210MB |
| PAskit-release.zip | 50-80MB |

### 推荐分发方式

1. **企业用户** - 使用安装程序（PAskit-installer.exe）
2. **个人用户** - 使用ZIP文件（PAskit-release.zip）
3. **便携版** - 直接使用可执行文件（PAskit.exe）

"""
