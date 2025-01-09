import { defineStore } from 'pinia';

interface UiState {
  isSidebarOpen: boolean;
  currentComponent: string | null;
  currentMapAction: string | null;
  selectedCoords: L.LatLng | null;
  selectedDestCoords: L.LatLng | null;
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
  }),
  actions: {
    resetCoords() {
      this.selectCoords(null);
      this.selectDestCoords(null);
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
