import { defineStore } from 'pinia';
import { usePointsStore } from './points';

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
    openSidebar(component: string) {
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
      this.selectedCoords = null;
      this.selectedDestCoords = null;
    },
  },
});
