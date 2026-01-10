# 📖 Askit. User Manual

Welcome to Askit. - AI-Powered Interactive Math Animation Teaching Software!

This manual will help you get started and make the most of Askit.'s powerful features.

---

## 🤖 Fine-tuned Model

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

## ⚙️ API Configuration Tutorial

### What is an API Key?

An **API Key (Application Programming Interface Key)** is a unique authentication token used to access AI service provider APIs. Think of it as a "key" that allows Askit. to communicate with AI services.

**Why do you need an API Key?**
- Askit. uses AI to understand your natural language instructions and generate math animation code
- AI services need to verify your identity to provide service
- API Key ensures only authorized users can use AI features

### What is a Base URL?

A **Base URL** is the access address of the AI service, telling Askit. which server to connect to for AI responses.

### Recommended Free API Services

#### 1. **OpenRouter** (Recommended)

- **Website**: https://openrouter.ai
- **Features**: Free credits for new users, supports multiple AI models, stable and reliable
- **Base URL**: `https://openrouter.ai/api/v1`

### How to Get an API Key

Using OpenRouter as an example:

1. **Register an Account**
   - Visit https://openrouter.ai
   - Click "Sign Up" in the top right corner
   - Register with email or Google account

2. **Get API Key**
   - After logging in, click your avatar
   - Select "API Keys" or "Settings"
   - Click "Create API Key"
   - Copy the generated key (format: `sk-or-v1-xxxxxxxxxxxxx`)
   - ⚠️ **Important**: Keep your API Key safe, don't share it

3. **Check Credits**
   - View remaining free credits on your account page

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

### What is the Physics Engine?

The **Physics Engine** is Askit.'s high-performance computing core, built with C++ and optimized for real-time physics simulation.

### Supported Features

#### 1. Rigid Body Collision (100 balls @ 12000+ FPS)
- Sphere, cube, cylinder collisions
- Gravity, friction simulation
- Hinge, spring constraints

#### 2. SPH Fluid (1000 particles @ 700 FPS)
- Smoothed Particle Hydrodynamics
- Water, oil liquid simulation

#### 3. ODE Solvers
- Euler, RK4, RK45 methods
- Adaptive step size control

#### 4. PDE Solvers
- Heat equation
- Wave equation
- Poisson equation

---

## 📸 Snapshot Feature

### What is the Snapshot Feature?

The **Snapshot Feature** automatically records the scene state of every frame in the animation, allowing AI to "see" and understand your animation content.

### How It Works

1. **Auto-capture every frame** - Records scene state at fixed intervals (default 0.02s)
2. **Build timeline cache** - Stores all frame snapshots in memory
3. **Provide context to AI** - AI can query scene state at any time point

### What Snapshots Record

- Object positions, rotations, scales
- Physics state (velocity, acceleration, energy)
- Variable values and control parameters
- Time information

---

## 🎬 Real-time Rendering

### What is Real-time Rendering?

High-performance rendering using OpenGL technology. Results display immediately after code execution.

### Core Features

- **Instant Preview** - No waiting for video rendering
- **Interactive Adjustment** - Modify parameters in real-time
- **Hardware Acceleration** - Smooth 60 FPS rendering

---

## ⏱️ Timeline Control

### What is Timeline Control?

A timeline control system for precise animation playback control.

### Features

- Display total animation duration
- Drag to jump to any time point
- Play/pause controls
- Playback speed adjustment

---

## 🎛️ Interactive Controls

### Supported Control Types

#### 1. **Slider**
- Adjust numeric parameters
- Set min/max values and step size

#### 2. **Button**
- Trigger specific actions
- Toggle states

#### 3. **Checkbox**
- On/off switches
- Show/hide objects

### Use Cases

- **Parameter Exploration**: Adjust gravity, friction in physics simulations
- **Comparison Experiments**: Compare different initial conditions
- **Interactive Demos**: Real-time adjustments during presentations
