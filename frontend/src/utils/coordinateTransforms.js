
/**
 * WGS84 Ellipsoid Parameters
 * a: Semi-major axis (km)
 * e2: First eccentricity squared
 */
const a = 6378.137; 
const e2 = 0.00669437999014;
const b = a * Math.sqrt(1 - e2);
const ep2 = (a ** 2 - b ** 2) / (b ** 2);

/**
 * Converts ECEF coordinates (km) to WGS84 Geodetic (degrees, meters)
 * Optimized for high-frequency render loops (60FPS+).
 * * @param {number} x - ECEF X in km
 * @param {number} y - ECEF Y in km
 * @param {number} z - ECEF Z in km
 * @returns {Array} [longitude (deg), latitude (deg), altitude (meters)]
 */
export const ecefToLla = (x, y, z) => {
  const p = Math.sqrt(x * x + y * y);
  const th = Math.atan2(a * z, b * p);
  
  const sinTh = Math.sin(th);
  const cosTh = Math.cos(th);
  
  const lon = Math.atan2(y, x);
  const lat = Math.atan2(
    z + ep2 * b * (sinTh ** 3),
    p - e2 * a * (cosTh ** 3)
  );
  
  const sinLat = Math.sin(lat);
  const N = a / Math.sqrt(1 - e2 * sinLat * sinLat);
  const altKm = (p / Math.cos(lat)) - N;

  // Deck.gl expects: [longitude, latitude, altitude in meters]
  return [
    lon * (180 / Math.PI), 
    lat * (180 / Math.PI), 
    altKm * 1000 
  ];
};