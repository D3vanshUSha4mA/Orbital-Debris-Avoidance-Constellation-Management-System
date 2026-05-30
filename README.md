## Running the System

Follow these steps to start the complete system.

---

### 1. Start the Backend

From the project root directory:

```bash
uvicorn main:app --reload
```

The backend will start at:

```
http://localhost:8000
```

---

### 2. Start the Telemetry Generator

Open a new terminal and run:

```bash
python telemetry_generator.py
```

This script generates satellite and debris telemetry and streams it to the backend.

---

### 3. Start the Frontend

Navigate to the frontend directory:

```bash
cd frontend/orbital-insight
```

Install dependencies (first time only):

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

The frontend will run at:

```
http://localhost:5173
```

---

### 4. Open the Dashboard

Open the following URL in your browser:

```
http://localhost:5173
```

The dashboard will start displaying satellites and debris once the telemetry generator is running.

