import L from 'leaflet';
import { defineStore } from 'pinia';

import { INITIAL_POS, INITIAL_ZOOM } from '@/components/Map/MapConstants';

interface UiState {
  isSidebarOpen: boolean;
  currentComponent: string | null;
  currentMapAction: string | null;
  selectedCoords: L.LatLng | null;
  selectedDestCoords: L.LatLng | null;
  currentPos: L.LatLng;
  currentZoom: number;
}

/**
 * Store for managing UI state.
 */
export const useUiStore = defineStore('ui', {
  state: (): UiState => ({
    isSidebarOpen: false,
    currentComponent: null,
    currentMapAction: null,
    selectedCoords: null,
    selectedDestCoords: null,
    currentPos: INITIAL_POS,
    currentZoom: INITIAL_ZOOM,
  }),
  actions: {
    resetCoords() {
      this.selectCoords(null);
      this.selectDestCoords(null);
    },
    /**
     * Set the current position of the map
     * @param coords
     * @returns
     */
    setPos(coords: UiState['currentPos']) {
      this.currentPos = coords;
      return coords;
    },
    /**
     * Parses the current hash on initial load
     */
    parseHash() {
      if (!window.location.hash) return;

      const params = new URLSearchParams(window.location.hash.substring(1)).get('map')?.split('/');

      if (!params) return;

      this.currentZoom = Number(params[0]);
      this.currentPos = new L.LatLng(Number(params[1]), Number(params[2]));
    },
    /**
     * Sets the current hash on the window for the map
     */
    setHash() {
      window.location.hash = `#map=${this.currentZoom}/${this.currentPos?.lat}/${this.currentPos?.lng}`;
    },
    /**
     * Sets the current zoom of the map
     * @param zoom
     * @returns
     */
    setZoom(zoom: UiState['currentZoom']) {
      this.currentZoom = zoom;
      return zoom;
    },
    /**
     * Select target coordinates for adding a spot
     * @param coords - L.LatLng
     */
    selectCoords(coords: UiState['selectedCoords']) {
      this.selectedCoords = coords;
      return coords;
    },
    /**
     * Select destination coordinates for adding a destination
     * @param coords - L.LatLng
     */
    selectDestCoords(coords: UiState['selectedDestCoords']) {
      this.selectedDestCoords = coords;
      return coords;
    },
    /**
     * Toggles the sidebar. If the sidebar is open, it resets the state.
     * Otherwise, it opens the sidebar with the specified component.
     *
     * @param component - The name of the component to display in the sidebar.
     */
    toggleSidebar(component: string) {
      // If the component should  change, reset and allow;
      // Else: Reset to close everything.
      if (component !== this.currentComponent) {
        this.reset();
      } else if (this.isSidebarOpen) {
        return this.closeSidebar();
      }

      this.openSidebar(component);
    },
    /**
     * Opens the sidebar with the specified component.
     * If there is a current map action and the component is not 'AddSpotForm', the sidebar will not open.
     *
     * @param component - The name of the component to display in the sidebar.
     */
    async openSidebar(component: string) {
      this.isSidebarOpen = true;
      this.currentMapAction = null;
      this.currentComponent = component;
    },
    /**
     * Closes the sidebar by resetting the state.
     */
    closeSidebar() {
      this.reset();
    },
    /**
     * Resets the UI state to its default values.
     */
    reset() {
      this.isSidebarOpen = false;
      this.currentComponent = null;
      this.currentMapAction = null;
      this.resetCoords();
    },
  },
});
