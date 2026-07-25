import React, { useMemo } from 'react';
import DeckGL from '@deck.gl/react';
import { MapView, FlyToInterpolator } from '@deck.gl/core';
import { ScatterplotLayer, GeoJsonLayer, PathLayer, PolygonLayer } from '@deck.gl/layers';
import { PathStyleExtension } from '@deck.gl/extensions';
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
      stroked: false,
      filled: true,
      getFillColor: [17, 24, 39, 255], // Match panel background
    }),
    new GeoJsonLayer({
      id: 'earth-borders',
      data: 'https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson',
      stroked: true,
      filled: false,
      lineWidthMinPixels: 1,
      getLineColor: [55, 65, 81, 255], // Match border color
    }),

    // Culled Threat Neighborhood Layer
    new ScatterplotLayer({
      id: 'debris-layer',
      data: debris,
      getPosition: d => d.coordinates,
      getFillColor: [239, 68, 68, 255], // Standard Red
      getRadius: 20000,
      radiusMinPixels: 2,
      radiusMaxPixels: 5,
    }),

    // Parametric Trajectory Prediction Paths (90 minutes dashed)
    new PathLayer({
      id: 'evasion-trajectory-layer',
      data: satellites,
      getPath: s => {
        const [lon, lat, alt] = s.coordinates;
        const path = [[lon, lat, alt]];
        // Approximate orbital path (frontend-only for visual representation)
        for (let i = 1; i <= 30; i++) {
            let nextLat = lat - Math.sin(i * 0.1) * 10;
            nextLat = Math.max(-85, Math.min(85, nextLat));
            path.push([lon + (i * 2), nextLat, alt]); 
        }
        return path;
      },
      getColor: [59, 130, 246, 150], // Professional blue
      widthUnits: 'pixels',               
      getWidth: 2,                        
      getDashArray: [4, 4],
      dashJustified: true,
      dashGapPickable: true,
      extensions: [new PathStyleExtension({dash: true})]
    }),

    // Constellation Node Network Layer
    new ScatterplotLayer({
      id: 'satellite-layer',
      data: satellites,
      getPosition: d => d.coordinates,
      getFillColor: d => {
        if (d.status === 'EVADING') return [245, 158, 11, 255]; // Standard Warning Orange
        return [59, 130, 246, 255]; // Professional Blue
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
        views={new MapView({ repeat: true })}
        viewState={{
          ...viewState,
          transitionInterpolator: viewState.transitionInterpolator === 'fly-to' 
            ? new FlyToInterpolator() 
            : null
        }}
        onViewStateChange={({ viewState }) => setViewState(viewState)}
        controller={{ dragRotate: false, doubleClickZoom: false }}
        layers={layers}
      />
    </div>
  );
}