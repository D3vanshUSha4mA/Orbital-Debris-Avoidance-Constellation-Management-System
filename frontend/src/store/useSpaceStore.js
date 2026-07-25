import { create } from 'zustand';

// Notice: persist middleware is completely removed. 
// The app will now always start with a clean slate.
export const useSpaceStore = create((set, get) => ({
  satellites: [],
  debris: [],
  warnings: [],
  activeManeuvers: [], 
  timestamp: null,
  isPolling: false,
  selectedSatId: null,

  viewState: {
    longitude: 45,
    latitude: 27,
    zoom: 1,
    maxZoom: 20,
    pitch: 30,
    transitionDuration: 0
  },

  setSelectedSat: (id) => set({ selectedSatId: id }),
  setViewState: (newViewState) => set({ viewState: newViewState }),

  flyToTarget: (lon, lat) => set({
    viewState: {
      longitude: lon,
      latitude: lat,
      zoom: 4,
      pitch: 45,
      transitionDuration: 2000,
      transitionInterpolator: 'fly-to'
    }
  }),

  executeManeuver: async (satelliteId) => {
    set(state => {
      if (state.activeManeuvers.some(m => m.id === satelliteId)) {
        return state;
      }

      const newManeuver = {
        id: satelliteId,
        startTime: Date.now(),
        status: 'BURNING'
      };

      return {
        // FIX 1: Update status to EVADING instead of filtering out the warning
        warnings: state.warnings.map(w => 
          w.obj_1 === satelliteId ? { ...w, status: 'EVADING' } : w
        ),
        activeManeuvers: [...state.activeManeuvers, newManeuver],
        satellites: state.satellites.map(sat => 
          sat.id === satelliteId 
            ? { 
                ...sat, 
                status: 'EVADING' 
              } 
            : sat
        )
      };
    });

    try {
      const payload = {
        satelliteId: satelliteId,
        maneuver_sequence: [
          {
            burn_id: `BURN-${Date.now()}`,
            burnTime: new Date().toISOString(),
            deltaV_vector: { x: 0.1, y: 0.2, z: 0.5 } 
          }
        ]
      };

      await fetch('http://localhost:8000/api/maneuver/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (error) {
      console.error("Maneuver tracking uplink failure:", error);
    }
  },

  fetchTelemetry: async (abortSignal) => {
    try {
      const response = await fetch('http://localhost:8000/api/visualization/snapshot', {
        signal: abortSignal
      });
      
      if (!response.ok) throw new Error(`Telemetry server status: ${response.status}`);
      const liveData = await response.json();

      const satellites = (liveData.satellites || []).map(sat => ({
        ...sat,
        type: 'SATELLITE',
        coordinates: [sat.lon, sat.lat, sat.alt_km * 1000]
      }));

      const threatDebrisIds = new Set((liveData.active_warnings || []).map(w => w.debris_id));
      const rawDebris = liveData.debris_cloud || [];
      
      const debrisWithDistances = rawDebris.map(deb => {
        const [id, lat, lon, alt_km] = deb;
        let minDistanceSq = Infinity;
        for (let i = 0; i < satellites.length; i++) {
          const sat = satellites[i];
          const dLon = lon - sat.lon;
          const dLat = lat - sat.lat;
          const distSq = (dLon * dLon) + (dLat * dLat); 
          if (distSq < minDistanceSq) {
            minDistanceSq = distSq;
          }
        }
        return { id, lat, lon, alt_km, minDistanceSq };
      });

      debrisWithDistances.sort((a, b) => a.minDistanceSq - b.minDistanceSq);

      const debris = debrisWithDistances
        .filter((deb, index) => threatDebrisIds.has(deb.id) || index < 500)
        .map(deb => ({
          id: deb.id,
          type: 'DEBRIS',
          coordinates: [deb.lon, deb.lat, deb.alt_km * 1000]
        }));

      const CRITICAL_DISTANCE_KM = 10.0;

      const incomingCriticals = (liveData.active_warnings || [])
          .filter(warn => warn.distance_km <= CRITICAL_DISTANCE_KM)
          .map(warn => ({
              obj_1: warn.obj_1 || warn.satellite_id,
              obj_2: warn.obj_2 || warn.debris_id,
              distance_km: warn.distance_km,
              status: warn.status || "CRITICAL"
          }));

      const existingWarnings = get().warnings;
      const activeManeuverIds = new Set(get().activeManeuvers.map(m => m.id));
      const mergedWarnings = [];

      // Only keep existing warnings that are still critical OR actively evading
      existingWarnings.forEach(w => {
         const stillCritical = incomingCriticals.some(inc => inc.obj_1 === w.obj_1 && inc.obj_2 === w.obj_2);
         const isEvading = activeManeuverIds.has(w.obj_1);
         if (stillCritical || isEvading) {
            mergedWarnings.push({...w, status: isEvading ? "EVADING" : w.status});
         }
      });

      // Add new warnings and update distances
      incomingCriticals.forEach(incoming => {
         const existingIndex = mergedWarnings.findIndex(w => w.obj_1 === incoming.obj_1 && w.obj_2 === incoming.obj_2);
         const isEvading = activeManeuverIds.has(incoming.obj_1);
         if (existingIndex === -1) {
            mergedWarnings.push({
               ...incoming,
               status: isEvading ? "EVADING" : incoming.status
            });
         } else {
            mergedWarnings[existingIndex].distance_km = incoming.distance_km;
         }
      });

      if (!abortSignal.aborted) {
        set({ 
          satellites, 
          debris, 
          warnings: mergedWarnings,
          timestamp: liveData.timestamp
        });
      }

    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error("Telemetry sync failure:", error.message);
      }
    }
  },

  startPolling: () => {
    if (get().isPolling) return;
    set({ isPolling: true });

    let abortController = new AbortController();
    const poll = async () => {
      await get().fetchTelemetry(abortController.signal);
      
      // FIX 3: Slowed down to 5000ms (5 seconds) to prevent gigabytes of backend logs
      get().timer = setTimeout(poll, 5000); 
    };

    poll();

    return () => {
      abortController.abort();
      clearTimeout(get().timer);
      set({ isPolling: false });
    };
  }
}));