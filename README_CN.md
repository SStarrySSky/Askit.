<div align="center">

**[English](README.md)** | **[中文](README_CN.md)**

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=60&pause=1000&color=000000&center=true&vCenter=true&repeat=false&width=250&height=80&lines=Ask%E2%9C%A6t." alt="Askit Logo" />

### 🚀 AI驱动的交互式数学动画教学软件

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![C++](https://img.shields.io/badge/C++-17-00599C?style=for-the-badge&logo=cplusplus&logoColor=white)](https://isocpp.org/)

[![HuggingFace](https://img.shields.io/badge/🤗%20Model-Askit--OLMo--32B-yellow?style=for-the-badge)](https://huggingface.co/SStarrySSky/Askit-OLMo-32B-Spatial-Thinking-Preview)
[![Website](https://img.shields.io/badge/🌐%20Website-askit.space-green?style=for-the-badge)](https://askit.space)
[![Docs](https://img.shields.io/badge/📖%20Docs-User%20Manual-orange?style=for-the-badge)](https://github.com/SStarrySSky/Askit./blob/main/Manual.md)

---

[🤖 微调模型](#-微调模型) • [⚙️ API配置](#️-api-配置教程) • [🔬 物理引擎](#-物理引擎功能) • [📸 快照功能](#-快照功能) • [🎬 实时渲染](#-实时渲染功能) • [⏱️ 进度条](#️-进度条功能) • [🎛️ 控件交互](#️-控件交互功能)

---

</div>

# 📖 Askit. 用户手册

欢迎使用 Askit. - AI驱动的交互式数学动画教学软件！

本手册将帮助您快速上手并充分利用 Askit. 的强大功能。

---

## 🤖 微调模型

<div align="center">

[![HuggingFace Model](https://img.shields.io/badge/🤗%20HuggingFace-Askit--OLMo--32B--Spatial--Thinking--Preview-yellow?style=for-the-badge)](https://huggingface.co/SStarrySSky/Askit-OLMo-32B-Spatial-Thinking-Preview)

</div>

### 什么是微调模型？

**微调模型**是专为 Askit. 定制调优的 AI 模型，基于 olmo-thinking 架构打造，经过大量物理和数学问题的训练，具有极强的空间理解能力和表达能力。

### 核心特性

#### 1. **空间理解能力**
- 深度理解三维空间中的物体位置关系
- 精确计算坐标、角度、距离等几何参数
- 自动推导物体的初始位置和运动轨迹

#### 2. **物理建模能力**
- 熟练掌握经典力学、电磁学、热力学等物理概念
- 能够将物理问题转化为 PhysicsBridge API 调用
- 支持复杂的多体系统和约束系统建模

#### 3. **高难度问题优化**
- 针对 CPhO（中国物理奥林匹克）难度问题特别优化
- 针对 IMO（国际数学奥林匹克）难度问题特别优化
- 能够处理需要深度推理的复杂问题

### 使用场景

1. **竞赛级物理问题**：CPhO、IPhO 等竞赛难度的物理模拟
2. **高级数学可视化**：IMO 级别的数学问题动画演示
3. **学术研究仿真**：需要精确物理建模的研究项目
4. **教学演示**：需要高质量动画的课堂教学

---

## ⚙️ API 配置教程

### 什么是 API Key？

**API Key（应用程序接口密钥）** 是一个唯一的身份验证令牌，用于访问 AI 服务提供商的 API。

### 免费 API 服务推荐

#### 1. **OpenRouter**（推荐）

- **官网**: https://openrouter.ai
- **特点**: 新用户有免费额度，支持多种 AI 模型，稳定可靠
- **Base URL**: `https://openrouter.ai/api/v1`

### 在 Askit. 中配置 API

1. **打开设置** - 点击右上角的 ⚙️ 设置按钮
2. **配置 API 信息**
   - API Provider: `Claude`
   - API Key: 您的 API Key
   - Base URL: `https://openrouter.ai/api/v1`
   - Model: `claude-3-5-sonnet-20241022`（推荐）
3. **保存并测试**

---

## 🔬 物理引擎功能

**物理引擎**是 Askit. 的高性能计算核心，基于 C++ 构建，专为实时物理模拟优化。

### 支持的功能

- **刚体碰撞**（100球 @ 12000+ FPS）
- **SPH流体**（1000粒子 @ 700 FPS）
- **ODE求解器**：Euler、RK4、RK45方法
- **PDE求解器**：热传导方程、波动方程、泊松方程

---

## 📸 快照功能

**快照功能**能够自动记录动画中每一帧的场景状态，让 AI 能够"看到"和理解您的动画内容。

---

## 🎬 实时渲染功能

使用 OpenGL 技术实现高性能的实时渲染，代码执行后立即显示结果，无需等待渲染。

---

## ⏱️ 进度条功能

时间轴控制系统，让您能够精确控制动画的播放进度，随时跳转到任意时间点查看效果。

---

## 🎛️ 控件交互功能

支持滑块、按钮、复选框等控件，在动画运行时动态调整参数，实时观察参数变化对动画的影响。

---

## 🛠️ 技术栈

<table>
<tr>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40" height="40"/>
<br><b>Python</b>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-original.svg" width="40" height="40"/>
<br><b>C++</b>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg" width="40" height="40"/>
<br><b>TypeScript</b>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" width="40" height="40"/>
<br><b>React</b>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/opengl/opengl-original.svg" width="40" height="40"/>
<br><b>OpenGL</b>
</td>
</tr>
</table>

---

## 📄 许可证

本项目采用 **GPL-3.0 License** - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<div align="center">

[![Website](https://img.shields.io/badge/Website-askit.space-blue?style=flat-square&logo=google-chrome)](https://askit.space)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Model-yellow?style=flat-square&logo=huggingface)](https://huggingface.co/SStarrySSky/Askit-OLMo-32B-Spatial-Thinking-Preview)
[![GitHub](https://img.shields.io/badge/GitHub-SStarrySSky-black?style=flat-square&logo=github)](https://github.com/SStarrySSky/Askit.)

**Made with ❤️ by Starry Sky**

</div>
