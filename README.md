# 🚀 Running the System (Backend)

The Project AETHER backend (physics engine, KD-Tree collision detection, and stateful evasion manager) is fully containerized for seamless deployment. The live telemetry streamer runs locally to feed real-world SGP4 data into the container.

---

## Prerequisites

* **Docker Desktop** installed and running.
* **Python 3.10+** installed locally (for the telemetry streamer).

---

# 1. Build and Run the Backend Container

Open your terminal in the root directory of the project and build the Docker image:

```bash
docker build -t aether-backend .
```

Start the container, mapping it to port `8000`:

```bash
docker run -p 8000:8000 aether-backend
```

The API is now live and actively listening for telemetry at:

```text
http://localhost:8000/api/telemetry
```

---

## Troubleshooting: "Port is already allocated"

If Docker fails to bind to port `8000`, a previous server instance is likely stuck in the background.

To clear it on Windows, open an **Administrator Command Prompt**:

### Find the PID

```bash
netstat -ano | findstr :8000
```

### Kill the PID

```bash
taskkill /PID <PID_NUMBER> /F
```

---

# 2. Launch the "Kobayashi Maru" Data Streamer

The backend requires a continuous feed of coordinate data to run the collision algorithms.

Open a **second, separate terminal** in the project root, activate your virtual environment, and start the streamer:

```bash
# Activate your virtual environment (Windows)
.\venv\Scripts\activate

# Start the real-time propagation engine
python live_streamer.py
```
