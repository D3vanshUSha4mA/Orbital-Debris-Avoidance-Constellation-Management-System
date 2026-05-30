import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function TelemetryHeatmap({ satellites }) {

  if (!satellites || satellites.length === 0) {
    return (
      <div style={{ color: '#888', textAlign: 'center', marginTop: '40px' }}>
        Awaiting telemetry feed...
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '300px', marginTop: '10px' }}>

      <ResponsiveContainer width="100%" height="100%">

        <BarChart
          data={satellites}
          margin={{ top: 20, right: 10, left: -20, bottom: 0 }}
        >

          <XAxis
            dataKey="id"
            stroke="#45a29e"
            tick={{ fill: '#c5c6c7', fontSize: 10 }}
          />

          <YAxis
            stroke="#45a29e"
            domain={[0, 50]}
            tick={{ fill: '#c5c6c7', fontSize: 12 }}
          />

          <Tooltip
            cursor={{ fill: 'rgba(255,255,255,0.1)' }}
            contentStyle={{
              backgroundColor: '#0b0c10',
              borderColor: '#45a29e',
              color: '#c5c6c7'
            }}
            itemStyle={{ color: '#66fcf1' }}
          />

          <Bar dataKey="fuel_kg" name="Fuel (kg)" radius={[4,4,0,0]}>

            {satellites.map((satellite, index) => {

              let color = '#2ecc71';

              if (satellite.fuel_kg <= 5.0) {
                color = '#e74c3c';
              } else if (satellite.fuel_kg <= 15.0) {
                color = '#f1c40f';
              }

              return <Cell key={index} fill={color} />;

            })}

          </Bar>

        </BarChart>

      </ResponsiveContainer>

    </div>
  );
}