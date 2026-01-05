"""
PAskit 打包发布完整指南

本文档说明如何将PAskit打包成可执行文件并发布给用户。
"""

# ============================================================================
# 方案1：PyInstaller（推荐）- 单个可执行文件
# ============================================================================

## 快速开始

### 步骤1：安装依赖
```bash
pip install pyinstaller
```

### 步骤2：运行打包脚本
```bash
python build.py
```

### 步骤3：测试可执行文件
```bash
# 在 dist/ 目录中找到 PAskit.exe
dist/PAskit.exe
```

### 步骤4：分发
- 文件位置：`release/PAskit-release.zip`
- 用户解压后直接运行 `PAskit.exe`

---

## 详细步骤

### 1. 准备环境

```bash
# 创建虚拟环境（可选但推荐）
python -m venv venv
venv\Scripts\activate

# 安装所有依赖
pip install -r requirements.txt
pip install pyinstaller
```

### 2. 构建可执行文件

```bash
# 方法A：使用build.py脚本（推荐）
python build.py

# 方法B：手动使用PyInstaller
pyinstaller --name=PAskit --onefile --windowed run.py
```

### 3. 测试可执行文件

```bash
# 在dist目录中测试
dist/PAskit.exe

# 验证：
# - 激活对话框正常显示
# - 输入激活码能正常激活
# - 主界面能正常加载
```

### 4. 创建安装程序（可选）

使用NSIS创建Windows安装程序：

```bash
# 安装NSIS
# 下载：https://nsis.sourceforge.io/

# 创建installer.nsi文件（见下方）
# 然后运行：
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
```

---

## 文件大小优化

### 减小可执行文件大小

```bash
# 使用UPX压缩（可选）
pip install upx

pyinstaller --name=PAskit --onefile --windowed \
  --upx-dir=path/to/upx run.py
```

### 典型文件大小
- 未优化：~200-300MB
- 优化后：~100-150MB
- 使用UPX：~50-80MB

---

## 发布清单

### 发布前检查

- [ ] 所有功能测试通过
- [ ] 激活系统正常工作
- [ ] 没有调试文件或日志
- [ ] 版本号已更新
- [ ] README和LICENSING文档已准备
- [ ] 生成激活码脚本已包含

### 发布文件结构

```
PAskit-release.zip
├── PAskit.exe              # 主程序
├── README.md               # 使用说明
├── LICENSING.md            # 许可证说明
├── INSTALL.txt             # 安装指南
└── generate_activation_code.py  # 激活码生成工具
```

---

## 用户安装步骤

1. 下载 `PAskit-release.zip`
2. 解压到任意文件夹
3. 双击 `PAskit.exe` 运行
4. 输入激活码激活
5. 开始使用

---

## 常见问题

### Q: 可执行文件太大怎么办？
A: 使用UPX压缩，或者分离数据文件

### Q: 如何更新版本？
A: 重新运行build.py，生成新的可执行文件

### Q: 如何添加应用图标？
A: 在build.py中指定 --icon=path/to/icon.ico

### Q: 如何隐藏控制台窗口？
A: 已在build.py中使用 --windowed 参数

### Q: 如何在启动时显示启动画面？
A: 使用 --splash=path/to/splash.png 参数

---

## 高级选项

### 创建NSIS安装程序

创建 `installer.nsi` 文件：

```nsis
; PAskit Installer
; 使用NSIS创建Windows安装程序

!include "MUI2.nsh"

Name "PAskit"
OutFile "PAskit-installer.exe"
InstallDir "$PROGRAMFILES\PAskit"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  File "dist\PAskit.exe"
  File "README.md"
  File "LICENSING.md"

  ; 创建开始菜单快捷方式
  CreateDirectory "$SMPROGRAMS\PAskit"
  CreateShortcut "$SMPROGRAMS\PAskit\PAskit.lnk" "$INSTDIR\PAskit.exe"
  CreateShortcut "$SMPROGRAMS\PAskit\Uninstall.lnk" "$INSTDIR\uninstall.exe"

  ; 创建卸载程序
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\PAskit.exe"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\LICENSING.md"
  Delete "$INSTDIR\uninstall.exe"
  RMDir "$INSTDIR"

  Delete "$SMPROGRAMS\PAskit\PAskit.lnk"
  Delete "$SMPROGRAMS\PAskit\Uninstall.lnk"
  RMDir "$SMPROGRAMS\PAskit"
SectionEnd
```

---

## 版本管理

### 更新版本号

编辑 `pyproject.toml`：

```toml
[project]
name = "paskit"
version = "1.0.0"  # 更新版本号
```

### 版本号格式

遵循语义化版本：`MAJOR.MINOR.PATCH`
- MAJOR: 重大功能更新
- MINOR: 新功能添加
- PATCH: 错误修复

---

## 发布渠道

### 1. 直接下载
- 在网站上提供 PAskit-release.zip 下载链接

### 2. GitHub Releases
```bash
# 创建GitHub release
gh release create v1.0.0 PAskit-release.zip
```

### 3. 应用商店
- Microsoft Store
- Chocolatey
- Winget

### 4. 企业分发
- 内部服务器
- 许可证管理系统

---

## 许可证和激活码分发

### 为用户生成激活码

```bash
# 为单个用户生成
python generate_activation_code.py \
  --name "John Doe" \
  --email "john@company.com" \
  --days 365

# 为团队生成并保存到文件
python generate_activation_code.py \
  --name "Team License" \
  --email "team@company.com" \
  --perpetual \
  --output licenses.txt
```

### 分发激活码

1. 通过邮件发送给用户
2. 在许可证管理门户中显示
3. 包含在安装包中（针对企业许可证）

---

## 监控和支持

### 收集反馈

- 在应用中添加反馈按钮
- 收集错误日志
- 跟踪激活统计

### 更新机制

考虑添加自动更新功能：
- 检查新版本
- 下载并安装更新
- 通知用户

---

## 安全建议

1. **代码签名**
   - 使用证书对可执行文件进行签名
   - 防止用户收到安全警告

2. **防病毒扫描**
   - 在VirusTotal上扫描可执行文件
   - 确保没有误报

3. **HTTPS分发**
   - 通过HTTPS提供下载
   - 使用CDN加速

4. **完整性检查**
   - 提供SHA256校验和
   - 用户可验证文件完整性

---

## 总结

### 快速发布流程

```
1. python build.py          # 构建可执行文件
2. 测试 dist/PAskit.exe     # 测试程序
3. 分发 release/PAskit-release.zip  # 发布给用户
4. 用户运行 PAskit.exe      # 用户安装
5. 用户输入激活码          # 用户激活
```

### 完整发布流程

```
1. 更新版本号
2. 运行所有测试
3. python build.py
4. 测试可执行文件
5. 创建NSIS安装程序（可选）
6. 生成激活码
7. 上传到发布服务器
8. 发送给用户
9. 收集反馈
10. 准备下一个版本
```

---

需要帮助？查看 LICENSING.md 了解激活系统详情。
