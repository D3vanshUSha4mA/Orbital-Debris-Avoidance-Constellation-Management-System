import React, { useEffect } from 'react';
import GlobeScene from './components/Globe/GlobeScene';
import { useSpaceStore } from './store/useSpaceStore';
import { Activity, Crosshair, ShieldAlert } from 'lucide-react';
import ManeuverTimeline from './components/HUD/ManeuverTimeline';

function App() {
  const startPolling = useSpaceStore(state => state.startPolling);
  const flyToTarget = useSpaceStore(state => state.flyToTarget);
  const executeManeuver = useSpaceStore(state => state.executeManeuver);
  
  const { satellites, debris, warnings } = useSpaceStore(state => ({
    satellites: state.satellites,
    debris: state.debris,
    warnings: state.warnings
  }));

  useEffect(() => {
    const cleanup = startPolling();
    return cleanup;
  }, [startPolling]);

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-space text-white font-mono selection:bg-hud-cyan selection:text-black">
      
      {/* 3D WebGL Background */}
      <GlobeScene />

      {/* CRT Scanline Effect Overlay */}
      <div className="pointer-events-none absolute inset-0 z-10 w-full h-full opacity-10 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,3px_100%] animate-scanline" />

      {/* Top Metrics Bar */}
      <header className="absolute top-0 left-0 w-full p-4 z-20 flex justify-between items-start pointer-events-none">
        <div className="flex items-center gap-4 border-b border-hud-cyan pb-2 pr-12 bg-gradient-to-r from-panel to-transparent backdrop-blur-sm">
          <Activity className="text-hud-cyan w-8 h-8 animate-pulse" />
          <div>
            <h1 className="text-2xl font-bold tracking-widest text-hud-cyan shadow-neon-cyan">ORBITAL INSIGHT</h1>
            <p className="text-xs text-hud-cyan/70 tracking-widest">ACM MISSION CONTROL</p>
          </div>
        </div>

        <div className="flex gap-8 bg-panel backdrop-blur-md px-6 py-3 rounded border border-hud-dim">
          <Metric label="ACTIVE SATS" value={satellites.length} color="text-hud-cyan" />
          <Metric label="WARNINGS" value={warnings.length} color="text-hud-warn" />
          <Metric label="DEBRIS" value={debris.length} color="text-hud-crit" />
        </div>
      </header>

      {/* Left Sidebar - Fleet Network */}
      <aside className="absolute top-24 left-4 bottom-16 w-80 z-20 flex flex-col gap-4 pointer-events-auto">
        <div className="bg-panel backdrop-blur-md border border-hud-dim h-full rounded p-4 flex flex-col">
          <h2 className="text-sm tracking-widest text-hud-cyan mb-4 flex items-center gap-2">
            <Crosshair className="w-4 h-4" /> FLEET NETWORK
          </h2>
          <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
            {satellites.map(sat => (
              <div 
                key={sat.id} 
                onClick={() => flyToTarget(sat.lon, sat.lat)}
                className="p-3 border border-hud-dim/50 rounded cursor-pointer hover:bg-hud-cyan/20 transition-colors group"
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="font-bold text-sm group-hover:text-white transition-colors">{sat.id}</span>
                  <span className={`text-xs ${sat.status === 'EVADING' ? 'text-hud-warn animate-pulse-fast' : 'text-hud-cyan'}`}>
                    {sat.status}
                  </span>
                </div>
                <div className="h-1 w-full bg-hud-dim rounded overflow-hidden">
                  <div className="h-full bg-hud-cyan w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </aside>

      {/* Right Sidebar - Conjunction Monitor */}
      <aside className="absolute top-24 right-4 bottom-16 w-96 z-20 flex flex-col gap-4 pointer-events-auto">
        <div className="bg-panel backdrop-blur-md border border-hud-crit/30 shadow-[0_0_15px_rgba(255,42,42,0.1)] h-full rounded p-4 flex flex-col">
          <h2 className="text-sm tracking-widest text-hud-crit mb-4 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 animate-pulse" /> CONJUNCTION LOGS
          </h2>
          <div className="space-y-3 flex-1 overflow-y-auto">
            {warnings.map((warn, i) => (
              <div key={i} className="p-3 border border-hud-crit/50 bg-hud-crit/5 rounded shadow-neon-crit">
                <div className="flex justify-between mb-1">
                  <span className="text-xs text-gray-400">TARGET:</span>
                  <span className="text-sm font-bold">{warn.obj_1}</span>
                </div>
                <div className="flex justify-between mb-1">
                  <span className="text-xs text-gray-400">THREAT:</span>
                  <span className="text-sm text-hud-crit">{warn.obj_2}</span>
                </div>
                <div className="flex justify-between items-center mt-2 pt-2 border-t border-hud-crit/20">
                  <span className="text-xs text-hud-warn">TCA DIST: {warn.distance_km}km</span>
                  
                  {/* THIS IS THE NEW BUTTON */}
                  <button 
                    onClick={() => {
                      // 1. Fly camera to the satellite
                      const targetSat = satellites.find(s => s.id === warn.obj_1);
                      if(targetSat) flyToTarget(targetSat.lon, targetSat.lat);
                      
                      // 2. Execute the burn command
                      executeManeuver(warn.obj_1);
                    }}
                    className="text-[10px] bg-hud-crit hover:bg-white hover:text-hud-crit text-black px-2 py-1 rounded font-bold transition-all cursor-pointer shadow-[0_0_10px_rgba(255,42,42,0.5)]"
                  >
                    EXECUTE BURN
                  </button>

                </div>
              </div>
            ))}
          </div>
        </div>
      </aside>

      {/* Bottom Center - Maneuver Timeline */}
      <aside className="absolute bottom-12 left-1/2 -translate-x-1/2 w-[600px] h-48 z-20 pointer-events-auto">
        <ManeuverTimeline />
      </aside>

      {/* Bottom Status Banner */}
      <div className="absolute bottom-0 left-0 w-full bg-hud-crit text-black py-1 z-30 text-center font-bold tracking-[0.2em] text-sm shadow-neon-crit overflow-hidden">
        <div className="animate-pulse">AUTONOMOUS INTERCEPT EVASION ENGINE ACTIVE</div>
      </div>
      
    </div>
  );
}

const Metric = ({ label, value, color }) => (
  <div className="flex flex-col items-center">
    <span className="text-[10px] text-gray-400 tracking-widest">{label}</span>
    <span className={`text-xl font-bold ${color}`}>{value}</span>
  </div>
);

export default App;