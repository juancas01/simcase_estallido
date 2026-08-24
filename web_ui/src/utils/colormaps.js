import * as d3 from 'd3-scale-chromatic';
import { scaleSequential } from 'd3-scale';

/**
 * Normalizes a value to a 0-1 range based on provided min and max.
 */
function normalize(value, min, max) {
  if (max === min) return 0;
  return Math.max(0, Math.min(1, (value - min) / (max - min)));
}

/**
 * Returns a hex color corresponding to Matplotlib's 'bone' colormap.
 * D3 does not have built-in 'bone', so we approximate it using an interpolated light-blue/gray sequential scale.
 * Or we can use d3.interpolatePuBuGn with custom inversion/adjustment.
 * Matplotlib 'bone' goes from Black -> Dark Purple/Blue -> Light Blue -> White.
 * A close proxy in D3 is interpolateGnBu or interpolateBone if we define it.
 * Let's manually define a proxy for 'bone' and 'gist_gray'
 */
const interpolateBone = (t) => {
  return d3.interpolateGreys(t); // Fallback until d3-interpolate is explicitly installed
};

const interpolateGistGray = (t) => {
  // Similar to standard gray scale, black to white
  return d3.interpolateGreys(t);
};

const interpolateWhRd = (t) => {
  // White (t=0) -> Red (t=1): reduce green and blue channels linearly
  const g = Math.round(255 * (1 - t));
  const b = Math.round(255 * (1 - t));
  return `rgb(255,${g},${b})`;
};

const interpolateWhGn = (t) => {
  // White (t=0) -> Green (t=1): rgb(255,255,255) -> rgb(22,163,74)
  const r = Math.round(255 - (255 - 22) * t);
  const g = Math.round(255 - (255 - 163) * t);
  const b = Math.round(255 - (255 - 74) * t);
  return `rgb(${r},${g},${b})`;
};

export const getColorScale = (colormap, min, max, value, invert = false) => {
  if (value === undefined || value === null) return 'transparent';
  
  let t = normalize(value, min, max);
  if (invert) {
    t = 1 - t;
  }

  switch (colormap) {
    case 'bone':
      return interpolateBone(t);
    case 'gist_gray':
      return interpolateGistGray(t);
    case 'WhRd':
      return interpolateWhRd(t);
    case 'WhGn':
      return interpolateWhGn(t);
    case 'RdYlGn':
      return d3.interpolateRdYlGn(t);
    case 'BuGn':
      return d3.interpolateBuGn(t);
    case 'OrRd':
      return d3.interpolateOrRd(t);
    default:
      return interpolateGistGray(t);
  }
};
