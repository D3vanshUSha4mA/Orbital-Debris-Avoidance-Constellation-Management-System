import React, { useMemo } from 'react';
import DeckGL from '@deck.gl/react';
import { _GlobeView as GlobeView, FlyToInterpolator } from '@deck.gl/core';
import { ScatterplotLayer, GeoJsonLayer, PathLayer, ArcLayer } from '@deck.gl/layers'; 
import { useSpaceStore } from '../../store/useSpaceStore';

export default function GlobeScene() {
  const satellites = useSpaceStore(state => state.satellites);
  const debris = useSpaceStore(state => state.debris);
  
  const viewState = useSpaceStore(state => state.viewState);
  const setViewState = useSpaceStore(state => state.setViewState);

  const layers = useMemo(() => [
    
    // Base Earth Geometry
    new GeoJsonLayer({
      id: 'earth-base',
      data: 'https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_land.geojson',
      stroked: true,
      filled: true,
      lineWidthMinPixels: 1,
      getLineColor: [0, 243, 255, 40],
      getFillColor: [5, 10, 21, 200], 
    }),

    // Culled Threat Neighborhood Layer
    new ScatterplotLayer({
      id: 'debris-layer',
      data: debris,
      getPosition: d => d.coordinates,
      getFillColor: [255, 42, 42, 200],
      getRadius: 15000,
      radiusMinPixels: 2,
      radiusMaxPixels: 5,
    }),

    // Vector Insertion Path Connection
    new ArcLayer({
      id: 'evasion-jump-arc',
      data: satellites.filter(s => s.status === 'EVADING'),
      getSourcePosition: d => [d.coordinates[0], d.coordinates[1], d.coordinates[2] - 1500000],
      getTargetPosition: d => d.coordinates,
      getSourceColor: [255, 42, 42, 200], 
      getTargetColor: [255, 170, 0, 255], 
      widthUnits: 'pixels',               
      getWidth: 4,
      getHeight: 0.2,                     
    }),

    // Parametric Trajectory Prediction Paths
    new PathLayer({
      id: 'evasion-trajectory-layer',
      data: satellites.filter(s => s.status === 'EVADING').map(s => {
        const [lon, lat, alt] = s.coordinates;
        const path = [];
        const nominalAlt = alt - 1500000; 

        for (let i = 0; i <= 30; i++) {
          const t = i / 30; 
          const projectedLon = lon + (t * 10); 
          const projectedAlt = nominalAlt + (1500000 * (1 - Math.pow(1 - t, 3))); 
          path.push([projectedLon, lat, projectedAlt]);
        }
        return { path };
      }),
      getPath: d => d.path,
      getColor: [255, 170, 0, 200], 
      widthUnits: 'pixels',               
      getWidth: 5,                        
      jointRounded: true,
      capRounded: true,
    }),

    // Constellation Node Network Layer
    new ScatterplotLayer({
      id: 'satellite-layer',
      data: satellites,
      getPosition: d => d.coordinates,
      getFillColor: d => {
        if (d.status === 'EVADING') return [255, 170, 0, 255]; 
        return [0, 243, 255, 255]; 
      },
      getRadius: 40000,
      radiusMinPixels: 4,
      radiusMaxPixels: 10,
      updateTriggers: {
        getFillColor: [satellites]
      },
      transitions: {
        getPosition: { duration: 800, easing: t => t * (2 - t) }, 
        getFillColor: { duration: 500 }
      }
    }),
    
    // Evasion Tracking Pulse Envelope
    new ScatterplotLayer({
      id: 'evasion-pulse-layer',
      data: satellites.filter(s => s.status === 'EVADING'),
      getPosition: d => d.coordinates,
      getFillColor: [255, 170, 0, 100],
      getRadius: 250000, 
      radiusMinPixels: 15,
      transitions: {
        getPosition: { duration: 800, easing: t => t * (2 - t) }
      }
    })

  ], [satellites, debris]);

  return (
    <div 
      className="absolute left-0 w-full z-0 bg-space"
      style={{ 
        top: '-10vh',     
        height: '110vh',  
        maskImage: 'linear-gradient(to bottom, black 70%, transparent 95%)',
        WebkitMaskImage: 'linear-gradient(to bottom, black 70%, transparent 95%)' 
      }}
    >
      <DeckGL
        views={new GlobeView({ resolution: 2 })}
        viewState={{
          ...viewState,
          transitionInterpolator: viewState.transitionInterpolator === 'fly-to' 
            ? new FlyToInterpolator() 
            : null
        }}
        onViewStateChange={({ viewState }) => setViewState(viewState)}
        controller={true}
        layers={layers}
      />
    </div>
  );
}