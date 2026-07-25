import React, { useEffect } from 'react';
import GlobeScene from './components/Globe/GlobeScene';
import { useSpaceStore } from './store/useSpaceStore';
import { Activity, Crosshair, ShieldAlert } from 'lucide-react';
import ManeuverTimeline from './components/HUD/ManeuverTimeline';
import BullseyePlot from './components/Dashboard/BullseyePlot';
import FleetTelemetry from './components/Dashboard/FleetTelemetry';

function App() {
  const startPolling = useSpaceStore(state => state.startPolling);
  const flyToTarget = useSpaceStore(state => state.flyToTarget);
  const executeManeuver = useSpaceStore(state => state.executeManeuver);
  
  const { satellites, debris, warnings, selectedSatId, setSelectedSatId } = useSpaceStore(state => ({
    satellites: state.satellites,
    debris: state.debris,
    warnings: state.warnings,
    selectedSatId: state.selectedSatId,
    setSelectedSatId: state.setSelectedSatId
  }));

  useEffect(() => {
    const cleanup = startPolling();
    return cleanup;
  }, [startPolling]);

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-space text-gray-200 font-sans selection:bg-hud-blue selection:text-white">
      
      {/* 2D Map Background */}
      <GlobeScene />

      {/* Top Metrics Bar */}
      <header className="absolute top-0 left-0 w-full p-4 z-20 flex justify-between items-start pointer-events-none">
        <div className="flex items-center gap-4 border-b-2 border-hud-cyan pb-2 pr-12 bg-panel shadow-lg rounded-br-lg">
          <Activity className="text-hud-cyan w-6 h-6 ml-4" />
          <div>
            <h1 className="text-xl font-extrabold tracking-widest text-white mt-2">ORBITAL INSIGHT</h1>
            <p className="text-[10px] text-gray-400 tracking-widest mb-2 font-mono">NASA ACM MISSION CONTROL</p>
          </div>
        </div>

        <div className="flex gap-8 bg-panel shadow-lg px-6 py-3 rounded-bl-lg border-b-2 border-hud-cyan">
          <Metric label="ACTIVE SATS" value={satellites.length} color="text-hud-cyan" />
          <Metric label="WARNINGS" value={warnings.length} color="text-hud-warn" />
          <Metric label="DEBRIS" value={debris.length} color="text-hud-crit" />
        </div>
      </header>

      {/* Left Sidebar - Fleet Network */}
      <aside className="absolute top-24 left-4 bottom-16 w-80 z-20 flex flex-col gap-4 pointer-events-auto">
        <div className="bg-panel border border-hud-dim shadow-xl h-full rounded-xl p-4 flex flex-col">
          <h2 className="text-xs font-bold tracking-widest text-gray-300 mb-4 flex items-center gap-2 border-b border-hud-dim pb-2">
            <Crosshair className="w-4 h-4 text-hud-cyan" /> FLEET NETWORK
          </h2>
          <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
            {satellites.map(sat => (
              <div 
                key={sat.id} 
                onClick={() => { flyToTarget(sat.lon, sat.lat); setSelectedSatId(sat.id); }}
                className={`p-3 rounded border cursor-pointer transition-colors group ${selectedSatId === sat.id ? 'border-hud-cyan bg-hud-cyan/10' : 'border-hud-dim/30 hover:bg-white/5'} font-mono`}
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="font-bold text-sm text-gray-200">{sat.id}</span>
                  <span className={`text-xs font-bold ${sat.status === 'EVADING' ? 'text-hud-warn' : 'text-hud-cyan'}`}>
                    {sat.status}
                  </span>
                </div>
                <div className="h-1 w-full bg-hud-dim rounded overflow-hidden">
                  <div className="h-full bg-hud-cyan w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 h-[280px]">
              <FleetTelemetry satellites={satellites} />
          </div>
        </div>
      </aside>

      {/* Right Sidebar - Conjunction Monitor */}
      <aside className="absolute top-24 right-4 bottom-16 w-96 z-20 flex flex-col gap-4 pointer-events-auto">
        <div className="bg-panel border border-hud-crit/20 shadow-xl h-full rounded-xl p-4 flex flex-col">
          <h2 className="text-xs font-bold tracking-widest text-gray-300 mb-4 flex items-center gap-2 border-b border-hud-dim pb-2">
            <ShieldAlert className="w-4 h-4 text-hud-crit" /> CONJUNCTION LOGS
          </h2>
          <div className="space-y-3 flex-1 overflow-y-auto font-mono custom-scrollbar pr-2">
            {warnings.map((warn, i) => (
              <div key={i} className="p-3 border border-hud-crit/30 bg-black/40 rounded shadow-sm">
                <div className="flex justify-between mb-1">
                  <span className="text-xs text-gray-400">TARGET:</span>
                  <span className="text-sm font-bold text-white">{warn.obj_1}</span>
                </div>
                <div className="flex justify-between mb-1">
                  <span className="text-xs text-gray-400">THREAT:</span>
                  <span className="text-sm font-bold text-hud-crit">{warn.obj_2}</span>
                </div>
                <div className="flex justify-between items-center mt-3 pt-2 border-t border-hud-crit/20">
                  <span className="text-xs text-hud-warn font-bold">{warn.distance_km}km TCA</span>
                  
                  {/* THIS IS THE NEW BUTTON */}
                  <button 
                    onClick={() => {
                      const targetSat = satellites.find(s => s.id === warn.obj_1);
                      if(targetSat) flyToTarget(targetSat.lon, targetSat.lat);
                      executeManeuver(warn.obj_1);
                    }}
                    className="text-[10px] bg-hud-crit hover:bg-red-700 text-white px-3 py-1.5 rounded font-bold transition-all cursor-pointer shadow-md"
                  >
                    EXECUTE MANEUVER
                  </button>

                </div>
              </div>
            ))}
          </div>
          <div className="mt-4">
              <BullseyePlot 
                  activeWarnings={warnings} 
                  selectedSatellite={satellites.find(s => s.id === selectedSatId)} 
              />
          </div>
        </div>
      </aside>

      {/* Bottom Center - Maneuver Timeline */}
      <aside className="absolute bottom-12 left-1/2 -translate-x-1/2 w-[600px] h-48 z-20 pointer-events-auto">
        <ManeuverTimeline />
      </aside>

      {/* Bottom Status Banner */}
      <div className="absolute bottom-0 left-0 w-full bg-hud-cyan text-black py-1.5 z-30 text-center font-bold tracking-[0.2em] text-xs shadow-md">
        <div>AUTONOMOUS INTERCEPT EVASION ENGINE ACTIVE</div>
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