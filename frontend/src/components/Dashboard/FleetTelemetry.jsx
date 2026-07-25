import React from 'react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export default function FleetTelemetry({ satellites }) {
  // Aggregate fuel
  const totalInitialFuel = satellites.length > 0 ? satellites.length * 50.0 : 50.0;
  const currentTotalFuel = satellites.reduce((acc, sat) => acc + (sat.fuel_kg || 50.0), 0);
  const fuelPercentage = totalInitialFuel > 0 ? (currentTotalFuel / totalInitialFuel) * 100 : 100;
  
  // Dummy data for Delta-V Cost Analysis Graph (Time vs Fuel Consumed)
  const costData = [
    { time: 'T-60m', consumed: 0.0, evasions: 0 },
    { time: 'T-45m', consumed: 0.4, evasions: 1 },
    { time: 'T-30m', consumed: 1.2, evasions: 2 },
    { time: 'T-15m', consumed: 1.5, evasions: 4 },
    { time: 'NOW', consumed: Math.max(1.5, totalInitialFuel - currentTotalFuel).toFixed(2), evasions: 5 },
  ];

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Fleet Fuel Gauge */}
      <div className="bg-panel border border-border rounded-lg p-4 shadow-md relative overflow-hidden">
        <h3 className="text-gray-300 text-xs font-bold tracking-widest mb-3 flex justify-between">
          <span>FLEET PROPELLANT</span>
          <span className={fuelPercentage < 10 ? 'text-hud-crit animate-pulse' : ''}>
            {fuelPercentage < 10 ? 'CRITICAL' : 'NOMINAL'}
          </span>
        </h3>
        <div className="relative h-6 w-full bg-space border border-border rounded overflow-hidden">
          <div 
            className={`absolute top-0 left-0 h-full transition-all duration-1000 ${fuelPercentage < 10 ? 'bg-hud-crit' : 'bg-hud-cyan'}`}
            style={{ width: `${Math.max(0, fuelPercentage)}%` }}
          />
          <div className="absolute inset-0 flex items-center justify-center mix-blend-difference">
            <span className="text-[10px] font-bold text-white tracking-widest">{fuelPercentage.toFixed(1)}% RETAINED</span>
          </div>
        </div>
        <div className="flex justify-between mt-2 text-[10px] text-gray-400 font-mono">
          <span>{currentTotalFuel.toFixed(1)} kg</span>
          <span>{totalInitialFuel.toFixed(1)} kg</span>
        </div>
      </div>

      {/* Delta-V Cost Analysis Graph */}
      <div className="bg-panel border border-border rounded-lg p-4 shadow-md flex-1 flex flex-col relative overflow-hidden">
        <h3 className="text-gray-300 text-xs font-bold tracking-widest mb-2">Δv COST ANALYSIS (kg)</h3>
        <div className="flex-1 w-full -ml-4 mt-2 font-mono">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={costData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorConsumed" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.5}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
              <XAxis dataKey="time" stroke="#9CA3AF" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="#9CA3AF" fontSize={10} tickLine={false} axisLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '4px' }}
                itemStyle={{ color: '#3B82F6', fontSize: '12px' }}
                labelStyle={{ color: '#F3F4F6', fontSize: '10px' }}
              />
              <Area type="monotone" dataKey="consumed" stroke="#3B82F6" strokeWidth={2} fillOpacity={1} fill="url(#colorConsumed)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
