import React from 'react';
import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip } from 'recharts';

export default function BullseyePlot({ activeWarnings, selectedSatellite }) {
  if (!selectedSatellite) return (
      <div className="h-64 w-full bg-panel border border-border rounded-lg p-4 flex items-center justify-center text-gray-500 text-sm font-mono shadow-md">
          SELECT SATELLITE TO INITIALIZE RADAR
      </div>
  );

  const warnings = activeWarnings.filter(w => w.obj_1 === selectedSatellite.id);
  
  if (warnings.length === 0) {
    return (
      <div className="h-64 w-full bg-panel border border-border rounded-lg p-4 shadow-md flex items-center justify-center text-gray-500 text-sm font-mono">
        NO ACTIVE THREATS IN ORBITAL SECTOR.
      </div>
    );
  }

  // Distribute approaching debris circularly for the radar map
  const data = warnings.map((w, index) => {
     const threatLevel = Math.max(0, 100 - (w.distance_km * 2)); 
     return {
        debrisId: w.obj_2,
        threatLevel: threatLevel,
        distance: w.distance_km,
        angle: (index * (360 / warnings.length)) % 360 
     };
  });

  return (
    <div className="h-64 w-full bg-panel border border-border rounded-lg p-4 shadow-md relative overflow-hidden">
      <h3 className="text-gray-300 text-xs font-bold tracking-widest mb-2 border-b border-border pb-1">CONJUNCTION RADAR</h3>
      <div className="h-48 w-full font-mono">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
              <PolarGrid stroke="#374151" />
              <PolarAngleAxis dataKey="debrisId" tick={{ fill: '#9CA3AF', fontSize: 10 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar
                name="Threat Level"
                dataKey="threatLevel"
                stroke="#EF4444"
                fill="#EF4444"
                fillOpacity={0.6}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#111827', borderColor: '#EF4444', borderRadius: '4px' }}
                itemStyle={{ color: '#EF4444', fontSize: '12px' }}
                labelStyle={{ color: '#F3F4F6', fontSize: '10px' }}
                formatter={(value, name, props) => [`${props.payload.distance.toFixed(2)} km`, 'Distance']}
              />
            </RadarChart>
          </ResponsiveContainer>
      </div>
    </div>
  );
}
