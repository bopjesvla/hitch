import { LatLng } from 'leaflet';

export const OPACITY_BY_RATING = {
  1: 0.3,
  2: 0.4,
  3: 0.6,
  4: 0.8,
  5: 0.8,
};

export const COLOR_BY_RATING = {
  1: 'red',
  2: 'orange',
  3: 'yellow',
  4: 'lightgreen',
  5: 'lightgreen',
};

export const INITIAL_POS = new LatLng(51.505, -0.09);
export const INITIAL_ZOOM = 13;
