# PAskit - AI Interactive Teaching Software

AI驱动的交互式数学和物理教学软件，使用ManimGL进行实时可视化。

## 项目状态

🚧 **当前处于早期开发阶段**

### 已完成
- ✅ 项目结构搭建
- ✅ ManimGL安装和配置
- ✅ 核心基础设施（config, logger, events）
- ✅ manim_bridge模块框架

### 进行中
- 🔄 ManimGL与PyQt6集成测试
- 🔄 PaskitScene wrapper实现

### 待完成
- ⏳ GUI框架（主窗口、聊天面板）
- ⏳ AI集成（多平台支持）
- ⏳ 代码执行引擎
- ⏳ 动画时间轴控制
- ⏳ Manim控件系统

## 架构

### 技术栈
- **GUI**: PyQt6
- **渲染**: ManimGL（魔改版）
- **AI**: 多平台支持（OpenAI, Anthropic, Ollama）
- **Python**: 3.11

### 核心组件
1. **manim_bridge** - ManimGL与PyQt6集成层
2. **gui** - 用户界面
3. **ai** - AI提供商集成
4. **execution** - 代码执行引擎
5. **controls** - 场景控件系统

## 安装

```bash
# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 架构变更说明

**重要**: 本项目最初计划使用完全自定义的OpenGL渲染引擎，但已改为基于ManimGL的魔改方案。

- ❌ 自定义OpenGL渲染引擎 → ✅ ManimGL
- ❌ 自定义动画系统 → ✅ Manim动画系统
- ❌ 自定义基础图形 → ✅ Manim Mobjects

`src/rendering/` 目录下的代码将被废弃，改为使用ManimGL。

## 开发计划

详见 `C:\Users\gqc_5\.claude\plans\graceful-questing-backus.md`
