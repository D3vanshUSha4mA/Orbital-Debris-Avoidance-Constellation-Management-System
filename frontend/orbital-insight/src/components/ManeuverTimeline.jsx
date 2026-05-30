import React from 'react';

export default function ManeuverTimeline({ maneuvers }) {
  // If there are no maneuvers, show the standby message
  if (!maneuvers || maneuvers.length === 0) {
    return (
      <div style={{ color: '#888', textAlign: 'center', marginTop: '40px' }}>
        No maneuvers scheduled. Standing by...
      </div>
    );
  }

  return (
    <div style={{ overflowY: 'auto', height: '85%', marginTop: '10px', paddingRight: '5px' }}>
      {maneuvers.map((maneuver, index) => (
        <div 
          key={index} 
          style={{ 
            marginBottom: '15px', 
            backgroundColor: '#0b0c10', 
            padding: '10px', 
            borderRadius: '4px', 
            // If there's a conflict, make the left border red. Otherwise, cyan.
            borderLeft: maneuver.hasConflict ? '4px solid #e74c3c' : '4px solid #45a29e' 
          }}
        >
          {/* Header Row: Satellite ID and Time */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: '#66fcf1', fontWeight: 'bold' }}>{maneuver.satelliteId}</span>
            <span style={{ color: '#c5c6c7', fontSize: '0.9em' }}>
              {new Date(maneuver.burnTime).toLocaleTimeString()}
            </span>
          </div>
          
          {/* The Gantt-Style Visual Blocks */}
          <div style={{ display: 'flex', height: '24px', width: '100%', backgroundColor: '#1f2833', borderRadius: '3px', overflow: 'hidden' }}>
            {/* The Burn Block */}
            <div style={{ width: '15%', backgroundColor: '#e74c3c', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7em', color: '#fff', fontWeight: 'bold' }}>
              BURN
            </div>
            {/* The 600-Second Cooldown Block */}
            <div style={{ width: '85%', backgroundColor: '#f1c40f', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7em', color: '#000', fontWeight: 'bold', opacity: 0.9 }}>
              600s COOLDOWN LOCK
            </div>
          </div>

          {/* Conflict Warning Flag */}
          {maneuver.hasConflict && (
            <div style={{ color: '#e74c3c', fontSize: '0.8em', marginTop: '8px', fontWeight: 'bold' }}>
              ⚠️ WARNING: LOS Blackout Conflict Detected!
            </div>
          )}
        </div>
      ))}
    </div>
  );
}