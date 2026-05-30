import React from 'react';
import {
  ScatterChart, Scatter, XAxis, YAxis, ZAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceDot
} from 'recharts';

export default function ConjunctionBullseye({ conjunctions }) {

  if (!conjunctions || conjunctions.length === 0) {
    return (
      <div style={{ color: "#888", textAlign: "center", marginTop: "40px" }}>
        No active conjunction threats
      </div>
    );
  }

  const satelliteId = conjunctions[0].satellite_id;

  return (
    <div style={{ width: "100%", height: "320px" }}>

      <div style={{
        textAlign: "center",
        color: "#66fcf1",
        marginBottom: "5px",
        fontWeight: "bold"
      }}>
        Satellite: {satelliteId}
      </div>

      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>

          <CartesianGrid strokeDasharray="3 3" stroke="#45a29e" opacity={0.3} />

          <XAxis
            type="number"
            dataKey="dx"
            domain={[-10, 10]}
            stroke="#45a29e"
            tick={{ fill: '#c5c6c7' }}
          />

          <YAxis
            type="number"
            dataKey="dy"
            domain={[-10, 10]}
            stroke="#45a29e"
            tick={{ fill: '#c5c6c7' }}
          />

          <ZAxis
            type="number"
            dataKey="distance"
            range={[50, 150]}
          />

          <Tooltip />

          {/* Satellite center */}
          <ReferenceDot x={0} y={0} r={6} fill="#66fcf1" />

          <Scatter data={conjunctions}>

            {conjunctions.map((entry, index) => {

              let color = '#2ecc71';

              if (entry.distance < 1.0) color = '#e74c3c';
              else if (entry.distance <= 5.0) color = '#f1c40f';

              return <Cell key={index} fill={color} />;
            })}

          </Scatter>

        </ScatterChart>
      </ResponsiveContainer>

    </div>
  );
}