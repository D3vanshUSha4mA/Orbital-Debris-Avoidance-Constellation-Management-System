<div id="top"></div>

<div align="center">

[![Contributors](https://img.shields.io/github/contributors/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System?style=for-the-badge)](https://github.com/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System/graphs/contributors)
[![Forks](https://img.shields.io/github/forks/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System?style=for-the-badge)](https://github.com/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System/network/members)
[![Stars](https://img.shields.io/github/stars/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System?style=for-the-badge)](https://github.com/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System/stargazers)
[![Issues](https://img.shields.io/github/issues/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System?style=for-the-badge)](https://github.com/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System/issues)
[![License](https://img.shields.io/github/license/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System?style=for-the-badge)](https://github.com/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System/blob/main/LICENSE)

<br>

# 🛰️ AETHER

### Autonomous Constellation Manager

### Real-Time Orbital Collision Avoidance & Fleet Management System

*A full-stack mission control platform capable of ingesting live satellite telemetry, predicting future conjunctions, autonomously planning collision avoidance maneuvers, and visualizing orbital environments in real time.*

<br>

<img src="images/showcase.png" width="950" alt="AETHER Dashboard">

</div>

---

# Table of Contents

- [About The Project](#about-the-project)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Physics & Algorithms](#physics--algorithms)
- [Performance & Benchmarking](#performance--benchmarking)
- [Project Structure](#project-structure)
- [Screenshot](#screenshot)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Future Improvements](#future-improvements)
- [License](#license)

---

# About The Project

Modern satellite constellations contain thousands of spacecraft operating within densely populated orbital shells. Predicting orbital conjunctions in real time requires continuously propagating trajectories, efficiently searching nearby objects, and responding before potential collisions occur.

**AETHER** is a real-time orbital collision avoidance system that combines orbital mechanics, numerical integration, spatial indexing, asynchronous backend services, and an interactive Deck.GL visualization dashboard into a unified mission-control platform.

The system continuously streams live satellite telemetry, predicts future conjunctions using Runge-Kutta integration, detects potential collisions through KD-Tree spatial partitioning, and autonomously executes avoidance maneuvers whenever predefined safety thresholds are exceeded.

---

# Key Features

## 🛰️ Live Telemetry Ingestion

- Fetches live Starlink and Debris TLEs directly from Celestrak
- Continuous 1 Hz telemetry updates with resilient local-fallback parsing
- Skyfield-based orbital propagation
- Real-time ECI-to-Lat/Lon conversion using accurate GMST math

---

## ☄️ Synthetic Debris Simulation

Generates dynamic fragmentation clouds and "rogue" intercepting orbits for stress-testing collision detection algorithms.

Features include:
- Targeted rogue debris generation for guaranteed interception testing
- Uses SGP4 for background debris and RK4 for custom high-velocity rogue objects
- Configurable cloud sizes
- Dynamic trajectory visualization

---

## 📡 Predictive Orbital Physics

Predicts future satellite positions using high-precision numerical integration.

Includes:
- RK4 orbital propagation (modeling J2 perturbations)
- Configurable fine-grained prediction step sizes (e.g. 30s intervals)
- 24-hour conjunction prediction
- Continuous state updates and dynamic blackout zone forecasting

---

## ⚠️ Collision Detection Engine

Efficiently detects conjunctions using advanced spatial indexing.

Features:
- SciPy cKDTree for high-load object partitioning
- Nearest-neighbor sub-150ms search
- Immediate collision detection
- Dynamic 10km warning radius filtering

---

## 🚀 Autonomous Collision Avoidance

When conjunction thresholds are exceeded, the engine automatically computes avoidance maneuvers.

Current implementation:
- Full 3-Burn Phasing Maneuvers (Evasion, Reversal, Circularization)
- Automatic EOL (End of Life) Graveyard Orbit tracking based on mass depletion
- Dynamic Fleet Propellant deduction calculated strictly through $\Delta v$ physics
- Real-time telemetry feedback integration

---

## 🌍 Interactive Mission Control Dashboard

Professional, NASA-inspired matte visualization interface.

Includes:
- Interactive 2D Mercator Deck.GL Map
- Satellite tracking with active status highlighting
- Target-locked Conjunction Radar (Bullseye Plot)
- Live $\Delta v$ Cost Analysis Area Graphs
- Real-Time Fleet Propellant Heatmap Gauges

---

# System Architecture

The platform is divided into three independent services to maximize responsiveness and maintain real-time performance.

---

## 1. Telemetry Streamer

Acts as the external tracking station.

Responsibilities:
- Download Starlink and Iridium-33 Debris TLEs
- Propagate orbital states natively
- Generate synthetic tracking debris 
- Stream telemetry every second

---

## 2. FastAPI Backend

Serves as the mission-control engine.

Responsibilities:
- High-throughput telemetry ingestion
- Immediate collision detection ($O(\log N)$ complexity)
- Future prediction engine 
- Autonomous maneuver planning
- Exposing sanitized visualization snapshot APIs

---

## 3. React Dashboard

NASA-styled mission-control interface providing:
- 2D Deck.GL Earth visualization
- Conjunction Radar monitoring
- $\Delta v$ expenditure tracking
- Fleet Network management sidebar

Technology Stack:
- React
- Tailwind CSS (NASA Matte Theme)
- Deck.GL / React-Map-GL
- Recharts
- Zustand

---

# Physics & Algorithms

## Runge-Kutta 4th Order (RK4)

Future orbital positions are computed using fourth-order Runge-Kutta numerical integration, taking into account Earth's gravitational parameters and J2 perturbation.

Advantages:
- High numerical accuracy
- Stable orbital propagation
- Low accumulated integration error
- Accurate long-term trajectory prediction

---

## KD-Tree Spatial Partitioning

Checking every object against every other object requires

```math
O(N^2)
```

comparisons.

Instead, AETHER organizes orbital objects inside a SciPy `cKDTree`, reducing the search complexity to

```math
O(N \log N)
```

allowing thousands of orbital objects to be processed efficiently.

---

# Performance & Benchmarking

The mathematical engine is highly optimized for Kessler Syndrome orbital scenarios. You can verify the engine's performance by running the built-in benchmarking suite:

```bash
cd backend
python benchmark.py
```

Current benchmarking tests validate:
1. **$O(\log N)$ Spatial Indexing:** Proves the KD-tree can resolve 100,000 piece debris clouds against the constellation in `< 150ms`.
2. **Autopilot Maneuver Latency:** Proves the phasing astrodynamics algorithm calculates the complete 3-burn sequences in `< 10ms`.

---

# Project Structure

```text
Orbital-Debris-Avoidance-Constellation-Management-System/

│
├── backend/
│   ├── api/
│   ├── core/
│   ├── main.py
│   ├── benchmark.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── store/
│   │   └── styles/
│   ├── package.json
│   └── tailwind.config.js
│
├── telemetry_generator.py
│
├── images/
│   └── showcase.png
│
├── README.md
│
└── LICENSE
```

---

# Screenshot

<p align="center">

<img src="images/showcase.png" width="950" alt="AETHER Dashboard">

</p>

---

# Getting Started

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git

---

## Clone Repository

```bash
git clone https://github.com/D3vanshUSha4mA/Orbital-Debris-Avoidance-Constellation-Management-System.git
```

---

## Backend Setup

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

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Open:
```
http://localhost:3000
```

---

## Start Live Telemetry Streamer

```bash
python telemetry_generator.py
```

The dashboard will begin rendering satellites, debris objects, and conjunction warnings in real time.

---

# API Reference

## POST `/api/telemetry`

Receives live orbital telemetry.

Example payload:

```json
{
  "timestamp": "2026-06-29T15:23:46Z",
  "objects": [
    {
      "id": "STARLINK-1008",
      "type": "SATELLITE",
      "r": {
        "x": 4200.1,
        "y": -1200.4,
        "z": 5500.9
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

Returns the latest visualization state.

Example response:

```json
{
  "timestamp": "...",
  "satellites": [],
  "debris_cloud": [],
  "active_warnings": []
}
```

---

# Future Improvements

Planned enhancements include:

- WebSocket-based telemetry streaming
- Multi-constellation support
- GPU-accelerated orbital propagation
- Distributed simulation workers
- Machine learning-based conjunction prediction
- Historical replay mode
- Cloud-native deployment

---

# License

Distributed under the MIT License.

See the `LICENSE` file for more information.

---

<div align="center">

## Built With

**Python • FastAPI • React • Tailwind CSS • Deck.GL • Recharts • Skyfield • SciPy • NumPy • Zustand**

</div>