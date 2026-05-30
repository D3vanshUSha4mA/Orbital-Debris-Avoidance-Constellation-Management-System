import React, { useState, useEffect } from 'react';

import GroundTrackMap from './components/GroundTrackMap';
import TelemetryHeatmap from './components/TelemetryHeatmap';
import ConjunctionBullseye from './components/ConjunctionBullseye';
import ManeuverTimeline from './components/ManeuverTimeline';

import './App.css';

function App() {

  const [telemetry, setTelemetry] = useState({
    satellites: [],
    debris_cloud: [],
    conjunctions: [],
    maneuvers: []
  });

  useEffect(() => {

    const fetchSnapshot = async () => {
      try {

        const response = await fetch(
          'http://localhost:8000/api/visualization/snapshot'
        );

        const data = await response.json();

        setTelemetry({
          satellites: data.satellites || [],
          debris_cloud: data.debris_cloud || [],
          conjunctions: data.conjunctions || [],
          maneuvers: data.maneuvers || []
        });

      } catch (error) {
        console.error(
          "Failed to fetch telemetry. Is the Python backend running?",
          error
        );
      }
    };

    fetchSnapshot();
    const intervalId = setInterval(fetchSnapshot, 1000);

    return () => clearInterval(intervalId);

  }, []);

  // Identify the satellite currently involved in a conjunction
  const focusSatellite =
    telemetry.conjunctions.length > 0
      ? telemetry.conjunctions[0].satellite_id
      : null;

  return (
    <div className="dashboard-container">

      <header>
        <h1>Orbital Insight Visualizer</h1>
      </header>

      <main className="grid-layout">

        {/* Ground Track Map */}
        <section className="module map-module">

          <h2>Ground Track (Mercator Projection)</h2>

          <div
            style={{
              width: '100%',
              height: '500px',
              position: 'relative',
              marginTop: '10px'
            }}
          >

            {telemetry.satellites.length > 0 && (
              <GroundTrackMap
                satellites={telemetry.satellites}
                debrisCloud={telemetry.debris_cloud}
                focusSatellite={focusSatellite}   
              />
            )}

          </div>

          <p style={{ marginTop: '5px' }}>
            Tracking {telemetry.satellites.length} Sats &{' '}
            {telemetry.debris_cloud.length} Debris
          </p>

        </section>

        {/* Conjunction Plot */}
        <section className="module polar-module">

          <h2>Conjunction "Bullseye" Plot</h2>

          <ConjunctionBullseye
            conjunctions={telemetry.conjunctions}
          />

        </section>

        {/* Telemetry Heatmap */}
        <section className="module telemetry-module">

          <h2>Fleet Telemetry & Fuel</h2>

          <TelemetryHeatmap
            satellites={telemetry.satellites}
          />

        </section>

        {/* Maneuver Timeline */}
        <section className="module timeline-module">

          <h2>Maneuver Timeline (Gantt)</h2>

          <ManeuverTimeline
            maneuvers={telemetry.maneuvers}
          />

        </section>

      </main>

    </div>
  );
}

export default App;