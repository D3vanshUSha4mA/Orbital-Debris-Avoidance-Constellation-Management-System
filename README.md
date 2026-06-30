<div id="top"></div>

<div align="center">

[![Contributors](https://img.shields.io/github/contributors/YOUR_USERNAME/AETHER?style=for-the-badge)](https://github.com/YOUR_USERNAME/AETHER/graphs/contributors)
[![Forks](https://img.shields.io/github/forks/YOUR_USERNAME/AETHER?style=for-the-badge)](https://github.com/YOUR_USERNAME/AETHER/network/members)
[![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/AETHER?style=for-the-badge)](https://github.com/YOUR_USERNAME/AETHER/stargazers)
[![Issues](https://img.shields.io/github/issues/YOUR_USERNAME/AETHER?style=for-the-badge)](https://github.com/YOUR_USERNAME/AETHER/issues)
[![License](https://img.shields.io/github/license/YOUR_USERNAME/AETHER?style=for-the-badge)](https://github.com/YOUR_USERNAME/AETHER/blob/main/LICENSE)

<br>

# 🛰️ AETHER: Autonomous Constellation Manager

### Real-Time Orbital Collision Avoidance & Fleet Evasion System

*A high-fidelity full-stack mission control platform for real-time satellite telemetry ingestion, predictive orbital physics, collision detection, and autonomous orbital maneuver planning.*

<br>

<!-- ================= HERO IMAGE ================= -->

<img src="images/showcase.png" width="900" alt="AETHER Showcase">

*(Replace this with a screenshot or GIF of the dashboard.)*

</div>

---

# Table of Contents

- [About The Project](#about-the-project)
- [Core Features](#core-features)
- [System Architecture](#system-architecture)
- [Mathematical Implementation](#mathematical-implementation)
- [Performance & Scalability](#performance--scalability)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [API Reference](#api-reference)
- [Future Improvements](#future-improvements)
- [License](#license)

---

# About The Project

Modern satellite constellations contain thousands of spacecraft sharing densely populated orbital shells. Detecting conjunctions in real time requires continuously processing orbital telemetry, predicting future trajectories, and responding autonomously before potential collisions occur.

**AETHER** is a real-time orbital collision avoidance platform designed for the National Space Science Hackathon. The system ingests live satellite telemetry, predicts conjunctions using numerical integration, and visualizes the complete orbital environment through an interactive WebGL dashboard.

The project combines orbital mechanics, high-performance spatial indexing, asynchronous backend processing, and modern frontend visualization into a single mission-control platform.

---

# Core Features

## Live Telemetry

- Real-time Starlink TLE ingestion
- Automatic orbital propagation
- Continuous 1Hz telemetry updates
- Skyfield integration

---

## Orbital Physics

- RK4 numerical integration
- Future trajectory prediction
- Autonomous collision detection
- Orbital maneuver planning

---

## Collision Detection

- SciPy cKDTree spatial partitioning
- Real-time conjunction monitoring
- Immediate threat detection
- 24-hour future prediction

---

## Autonomous Evasion

- Automatic altitude adjustments
- Dynamic orbital rerouting
- Conjunction Data Message (CDM) generation
- Collision avoidance logic

---

## Interactive Dashboard

- React + Tailwind CSS
- React Three Fiber
- WebGL Earth visualization
- Real-time telemetry updates
- Live conjunction logs

---

# System Architecture

AETHER is divided into three independent services to maximize responsiveness and scalability.

---

## 1. Live Telemetry Streamer

The streamer acts as an external radar station.

Responsibilities:

- Downloads Starlink TLEs from Celestrak
- Computes position and velocity vectors
- Generates synthetic debris
- Sanitizes invalid numerical values
- Streams telemetry every second

---

## 2. FastAPI Backend

The backend serves as the mission control engine.

Responsibilities:

- High-speed telemetry ingestion
- Raw byte parsing
- Immediate conjunction detection
- Background future prediction
- Autonomous orbital maneuvers

Performance optimizations include:

- Raw request parsing
- Background workers
- Deep-copy simulation states
- GIL yielding during heavy physics calculations

---

## 3. React Dashboard

Mission control interface providing:

- 3D Earth visualization
- Live satellite tracking
- Debris cloud rendering
- Conjunction warnings
- Fleet status monitoring

Built using:

- React
- Tailwind CSS
- Zustand
- React Three Fiber

---

# Mathematical Implementation

## Runge-Kutta 4th Order (RK4)

Future satellite positions are calculated using fourth-order Runge-Kutta numerical integration.

Unlike simple linear extrapolation, RK4 accurately models continuously changing orbital trajectories.

Benefits:

- High numerical stability
- Accurate long-term prediction
- Reduced integration error

---

## KD-Tree Spatial Partitioning

Naively comparing every object against every other object requires

```math
O(N^2)
```

time.

Instead, AETHER organizes all orbital objects inside a SciPy cKDTree, reducing collision detection complexity to

```math
O(N \log N)
```

allowing thousands of objects to be processed efficiently on consumer hardware.

---

# Performance & Scalability

Current development configuration:

| Metric | Value |
|----------|--------|
| Satellites | 200 |
| Debris | 300 |
| Total Objects | 500 |
| Telemetry Rate | 1 Hz |
| Prediction Window | 24 Hours |

---

## Current Limitation

The orbital engine itself comfortably scales to over **10,000 tracked objects**.

Current bottleneck:

- Large JSON payloads (~2 MB/sec)
- Windows ↔ WSL2 Docker network fragmentation
- HTTP polling overhead

---

## Planned Scaling Roadmap

- Native Linux deployment
- Cloud-hosted backend
- WebSocket streaming
- Vectorized RK4 implementation
- NumPy optimization
- Distributed simulation workers

---

# Project Structure

```text
AETHER/

│
├── backend/
│   ├── main.py
│   ├── physics/
│   ├── api/
│   ├── models/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── store/
│   └── package.json
│
├── live_streamer.py
│
├── images/
│   └── showcase.png
│
├── README.md
│
└── LICENSE
```

---

# Screenshots

## Mission Control Dashboard

> Replace the image below with your dashboard screenshot or GIF.

<p align="center">

<img src="images/showcase.png" width="950" alt="AETHER Dashboard">

</p>

---

# Installation

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git

---

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/AETHER.git
```

---

## 2. Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --host 127.0.0.1 --port 8000
```

Backend documentation:

```
http://127.0.0.1:8000/docs
```

---

## 3. Frontend Setup

```bash
cd frontend

npm install

npm start
```

Frontend:

```
http://localhost:3000
```

---

## 4. Start Telemetry Streamer

```bash
python live_streamer.py
```

The dashboard will immediately populate with satellites, debris, and conjunction warnings.

---

# API Reference

## POST `/api/telemetry`

Receives live orbital telemetry.

Example payload:

```json
{
  "timestamp": "...",
  "objects": [
    {
      "id": "STARLINK-1008",
      "type": "satellite",
      "r": {
        "x": 4200,
        "y": -1200,
        "z": 5500
      },
      "v": {
        "x": 7.4,
        "y": -1.2,
        "z": 0.8
      }
    }
  ]
}
```

---

## GET `/api/visualization/snapshot`

Returns current visualization data.

Response:

- Satellites
- Debris
- Conjunction warnings
- Timestamp

---

# Future Improvements

Planned enhancements include:

- WebSocket telemetry streaming
- Multi-constellation support
- ML-based collision prediction
- Distributed physics engine
- GPU-accelerated orbital propagation
- Interactive maneuver planning
- Historical replay mode
- Space weather integration

---

# License

Distributed under the MIT License.

See `LICENSE` for more information.

---

<div align="center">

**Built With**

Python • FastAPI • React • Tailwind CSS • React Three Fiber • Skyfield • SciPy • NumPy • Zustand • Docker

</div>