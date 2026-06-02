import React from 'react';
import { useSpaceStore } from '../../store/useSpaceStore';
import { Clock } from 'lucide-react';

export default function ManeuverTimeline() {
  const activeManeuvers = useSpaceStore(state => state.activeManeuvers);

  return (
    <div className="w-full h-full bg-panel backdrop-blur-md border border-hud-dim rounded p-4 flex flex-col pointer-events-auto">
      
      {/* Header Panel */}
      <div className="flex justify-between items-center mb-4 border-b border-hud-dim/50 pb-2">
        <h2 className="text-sm tracking-widest text-hud-cyan flex items-center gap-2">
          <Clock className="w-4 h-4" /> MANEUVER TIMELINE <span className="text-[10px] text-gray-500 ml-2">GANTT</span>
        </h2>
        <div className="flex gap-4 text-[10px] font-bold tracking-wider">
          <div className="flex items-center gap-1"><div className="w-2 h-2 bg-hud-crit rounded-sm"></div> EVASION BURN</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 bg-orange-500 rounded-sm"></div> RECOVERY</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 bg-hud-dim rounded-sm"></div> COOLDOWN</div>
        </div>
      </div>

      {/* Temporal References */}
      <div className="flex pl-32 pr-4 text-[10px] text-gray-500 tracking-widest justify-between mb-2">
        <span>T-0</span>
        <span>T+30m</span>
        <span>T+60m</span>
        <span>T+90m</span>
        <span>T+120m</span>
      </div>

      {/* Gantt Tracking Area */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
        {activeManeuvers.length === 0 ? (
          <div className="w-full text-center text-xs text-gray-500 mt-8 tracking-widest">
            AWAITING MANEUVER COMMANDS...
          </div>
        ) : (
          activeManeuvers.map((maneuver) => (
            <div key={maneuver.id} className="flex items-center gap-4 group">
              <span className="w-28 text-xs font-bold truncate group-hover:text-hud-cyan transition-colors">
                {maneuver.id}
              </span>
              
              <div className="flex-1 h-4 bg-hud-dim/20 rounded border border-hud-dim/30 flex overflow-hidden">
                <div className="h-full bg-hud-crit w-[20%] animate-pulse-fast"></div>
                <div className="h-full bg-orange-500 w-[15%]"></div>
                <div className="h-full bg-hud-dim w-[45%]"></div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}