<div align="center">

**[English](README.md)** | **[中文](README_CN.md)**

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=60&pause=1000&color=000000&center=true&vCenter=true&repeat=false&width=250&height=80&lines=Ask%E2%9C%A6t." alt="Askit Logo" />

### 🚀 AI-Powered Interactive Math Animation Teaching Software

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![C++](https://img.shields.io/badge/C++-17-00599C?style=for-the-badge&logo=cplusplus&logoColor=white)](https://isocpp.org/)

[![HuggingFace](https://img.shields.io/badge/🤗%20Model-Askit--OLMo--32B-yellow?style=for-the-badge)](https://huggingface.co/SStarrySSky/Askit-OLMo-32B-Spatial-Thinking-Preview)
[![Website](https://img.shields.io/badge/🌐%20Website-askit.space-green?style=for-the-badge)](https://askit.space)
[![Docs](https://img.shields.io/badge/📖%20Docs-User%20Manual-orange?style=for-the-badge)](https://github.com/SStarrySSky/Askit./blob/main/Manual_EN.md)

---

[🤖 Fine-tuned Model](#-fine-tuned-model) • [⚙️ API Config](#️-api-configuration) • [🔬 Physics Engine](#-physics-engine) • [📸 Snapshot](#-snapshot-feature) • [🎬 Real-time Rendering](#-real-time-rendering) • [⏱️ Timeline](#️-timeline-control) • [🎛️ Interactive Controls](#️-interactive-controls)

---

</div>

# 📖 Askit. User Manual

Welcome to Askit. - AI-Powered Interactive Math Animation Teaching Software!

This manual will help you get started and make the most of Askit.'s powerful features.

---

## 🤖 Fine-tuned Model

<div align="center">

[![HuggingFace Model](https://img.shields.io/badge/🤗%20HuggingFace-Askit--OLMo--32B--Spatial--Thinking--Preview-yellow?style=for-the-badge)](https://huggingface.co/SStarrySSky/Askit-OLMo-32B-Spatial-Thinking-Preview)

</div>

### What is the Fine-tuned Model?

The **fine-tuned model** is an AI model custom-optimized for Askit., built on the OLMo-thinking architecture. Trained on extensive physics and mathematics problems, it possesses exceptional spatial understanding and expression capabilities.

### Core Features

#### 1. **Spatial Understanding**
- Deep understanding of object positions in 3D space
- Precise calculation of coordinates, angles, distances, and other geometric parameters
- Automatic derivation of initial positions and motion trajectories

#### 2. **Physics Modeling**
- Proficient in classical mechanics, electromagnetism, thermodynamics concepts
- Capable of translating physics problems into PhysicsBridge API calls
- Supports complex multi-body systems and constraint modeling

#### 3. **Advanced Problem Optimization**
- Specially optimized for CPhO (Chinese Physics Olympiad) level problems
- Specially optimized for IMO (International Mathematical Olympiad) level problems
- Capable of handling complex problems requiring deep reasoning

### Use Cases

1. **Competition-level Physics**: Physics simulations at CPhO, IPhO difficulty levels
2. **Advanced Math Visualization**: IMO-level mathematical problem animations
3. **Academic Research Simulation**: Research projects requiring precise physics modeling
4. **Teaching Demonstrations**: Classroom teaching requiring high-quality animations

---

## ⚙️ API Configuration

### What is an API Key?

An **API Key** is a unique authentication token used to access AI service provider APIs.

### Recommended Free API Services

#### 1. **OpenRouter** (Recommended)

- **Website**: https://openrouter.ai
- **Features**: Free credits for new users, supports multiple AI models, stable and reliable
- **Base URL**: `https://openrouter.ai/api/v1`

### Configuring API in Askit.

1. **Open Settings** - Click the ⚙️ settings button in the top right corner
2. **Configure API Information**
   - API Provider: `Claude`
   - API Key: Your API Key
   - Base URL: `https://openrouter.ai/api/v1`
   - Model: `claude-3-5-sonnet-20241022` (Recommended)
3. **Save and Test**

---

## 🔬 Physics Engine

The **Physics Engine** is Askit.'s high-performance computing core, built with C++ and optimized for real-time physics simulation.

### Supported Features

- **Rigid Body Collision** (100 balls @ 12000+ FPS)
- **SPH Fluid** (1000 particles @ 700 FPS)
- **ODE Solvers**: Euler, RK4, RK45 methods
- **PDE Solvers**: Heat equation, Wave equation, Poisson equation

---

## 📸 Snapshot Feature

The **Snapshot Feature** automatically records the scene state of every frame in the animation, allowing AI to "see" and understand your animation content.

---

## 🎬 Real-time Rendering

High-performance real-time rendering using OpenGL technology. Results are displayed immediately after code execution, no waiting for rendering required.

---

## ⏱️ Timeline Control

A timeline control system that allows you to precisely control animation playback progress and jump to any point in time to view effects.

---

## 🎛️ Interactive Controls

Supports sliders, buttons, checkboxes, and other controls to dynamically adjust parameters during animation runtime and observe the effects of parameter changes in real-time.

---

## 🛠️ Tech Stack

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

## 📄 License

This project is licensed under **GPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

[![Website](https://img.shields.io/badge/Website-askit.space-blue?style=flat-square&logo=google-chrome)](https://askit.space)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Model-yellow?style=flat-square&logo=huggingface)](https://huggingface.co/SStarrySSky/Askit-OLMo-32B-Spatial-Thinking-Preview)
[![GitHub](https://img.shields.io/badge/GitHub-SStarrySSky-black?style=flat-square&logo=github)](https://github.com/SStarrySSky/Askit.)

**Made with ❤️ by Starry Sky**

</div>
