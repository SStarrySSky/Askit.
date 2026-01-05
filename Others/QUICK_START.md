"""
PAskit 快速打包指南

只需3个命令即可打包发布！
"""

# ============================================================================
# 快速开始 - 3步打包
# ============================================================================

## 步骤1：安装PyInstaller

```bash
pip install pyinstaller
```

## 步骤2：运行打包脚本

```bash
python build.py
```

这个脚本会自动：
✓ 清理旧的构建文件
✓ 使用PyInstaller打包
✓ 创建发布目录
✓ 生成ZIP压缩包

## 步骤3：测试和发布

```bash
# 测试可执行文件
dist/PAskit.exe

# 发布给用户
# 文件位置：release/PAskit-release.zip
```

---

## 输出文件说明

打包完成后，你会得到：

```
PAskit/
├── dist/
│   └── PAskit.exe              # 单个可执行文件（可直接运行）
├── release/
│   ├── PAskit/                 # 发布目录
│   │   ├── PAskit.exe
│   │   ├── README.md
│   │   ├── LICENSING.md
│   │   ├── INSTALL.txt
│   │   └── generate_activation_code.py
│   └── PAskit-release.zip      # 压缩包（发给用户）
└── build/                      # 构建临时文件（可删除）
```

---

## 用户使用流程

### 用户收到 PAskit-release.zip

1. **解压**
   ```
   解压 PAskit-release.zip 到任意文件夹
   ```

2. **运行**
   ```
   双击 PAskit.exe
   ```

3. **激活**
   ```
   输入激活码 → 点击 Activate
   ```

4. **使用**
   ```
   开始使用PAskit！
   ```

---

## 生成激活码

### 为用户生成激活码

```bash
# 生成1年有效期的激活码
python generate_activation_code.py \
  --name "用户名" \
  --email "user@example.com" \
  --days 365

# 生成永久激活码
python generate_activation_code.py \
  --name "用户名" \
  --email "user@example.com" \
  --perpetual

# 生成并保存到文件
python generate_activation_code.py \
  --name "用户名" \
  --email "user@example.com" \
  --perpetual \
  --output licenses.txt
```

---

## 完整发布流程

### 第一次发布

```bash
# 1. 确保所有代码已提交
git status

# 2. 更新版本号（可选）
# 编辑 pyproject.toml 中的 version

# 3. 运行打包脚本
python build.py

# 4. 测试可执行文件
dist/PAskit.exe

# 5. 生成激活码
python generate_activation_code.py --name "Test" --email "test@example.com" --perpetual

# 6. 分发 release/PAskit-release.zip 给用户
```

### 后续更新

```bash
# 1. 修改代码
# 2. 测试
# 3. python build.py
# 4. 分发新的 PAskit-release.zip
```

---

## 常见问题

### Q: 可执行文件在哪里？
A: `dist/PAskit.exe` - 这是最终的可执行文件

### Q: 用户需要安装Python吗？
A: 不需要！可执行文件已包含所有依赖

### Q: 如何更新应用？
A: 重新运行 `python build.py`，生成新的可执行文件

### Q: 文件太大怎么办？
A: 正常大小是100-200MB，包含所有依赖

### Q: 如何添加应用图标？
A: 在 build.py 中修改 `--icon=src/assets/icons/app.ico`

### Q: 如何创建安装程序？
A: 查看 PACKAGING.md 中的NSIS部分

---

## 发布渠道

### 1. 直接下载（最简单）
- 上传 `PAskit-release.zip` 到网站
- 用户下载后解压运行

### 2. GitHub Releases
```bash
# 创建release
gh release create v1.0.0 release/PAskit-release.zip
```

### 3. 企业分发
- 内部服务器
- 许可证管理系统
- 自动更新服务

---

## 文件清单

发布前检查：

- [ ] PAskit.exe 能正常运行
- [ ] 激活对话框显示正确
- [ ] 激活码能正常验证
- [ ] 主界面能正常加载
- [ ] 所有功能正常工作
- [ ] README.md 已准备
- [ ] LICENSING.md 已准备
- [ ] 激活码生成脚本已包含

---

## 下一步

1. **立即打包**
   ```bash
   python build.py
   ```

2. **测试可执行文件**
   ```bash
   dist/PAskit.exe
   ```

3. **生成激活码**
   ```bash
   python generate_activation_code.py --name "Your Name" --email "your@email.com" --perpetual
   ```

4. **分发给用户**
   ```
   发送 release/PAskit-release.zip
   ```

---

## 更多信息

- 详细打包指南：查看 PACKAGING.md
- 许可证系统：查看 LICENSING.md
- 激活码生成：python generate_activation_code.py --help
"""
