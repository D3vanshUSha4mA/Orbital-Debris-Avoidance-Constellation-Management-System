import React from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer } from '@deck.gl/layers';
import { Map } from 'react-map-gl/maplibre';

const INITIAL_VIEW_STATE = {
  longitude: 0,
  latitude: 0,
  zoom: 1.5,
  pitch: 0,
  bearing: 0
};

export default function GroundTrackMap({
  satellites = [],
  debrisCloud = [],
  focusSatellite = null
}) {

  if (!satellites || !debrisCloud) {
    return null;
  }

  const debrisLayer = new ScatterplotLayer({
    id: 'debris-layer',
    data: debrisCloud,
    getPosition: d => [d[2], d[1]],
    getFillColor: [255, 65, 54, 180],
    getRadius: 20000,
    radiusMinPixels: 2,
    pickable: true
  });

  const satelliteLayer = new ScatterplotLayer({
    id: 'satellite-layer',
    data: satellites,

    getPosition: d => [d.lon, d.lat],

    // Highlight the conjunction satellite
    getFillColor: d =>
      d.id === focusSatellite
        ? [255, 0, 0, 255]      // highlighted satellite (red)
        : [46, 204, 113, 255],  // normal satellites (green)

    // Make the highlighted satellite larger
    getRadius: d =>
      d.id === focusSatellite
        ? 120000
        : 50000,

    radiusMinPixels: 4,
    pickable: true
  });

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        minHeight: '400px'
      }}
    >
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={[debrisLayer, satelliteLayer]}
        style={{ width: '100%', height: '100%' }}
      >
        <Map
          reuseMaps
          mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        />
      </DeckGL>
    </div>
  );
}