import { usePointsStore } from '@/stores/points';
import { useUiStore } from '@/stores/ui';
import L from 'leaflet';

const AddSpotButton = L.Control.extend({
  options: {
    position: 'topleft',
  },
  onAdd: () => {
    const controlDiv = L.DomUtil.create('div', 'leaflet-bar clear-none');
    const container = L.DomUtil.create('a', '!w-auto !h-auto px-2', controlDiv);
    container.href = 'javascript:void(0);';
    container.innerText = '📍 Add spot';

    container.onclick = function (e) {
      const uiStore = useUiStore();
      const pointsStore = usePointsStore();

      uiStore.closeSidebar();
      uiStore.currentMapAction = 'AddSpot';
      pointsStore.selectedPoint = undefined;

      L.DomEvent.stopPropagation(e);
    }

    // container.onclick = function (e) {
    //     if (window.location.href.includes('light')) {
    //         if (confirm('Do you want to be redirected to the full version where you can add spots?'))
    //             navigateTo('/');
    //         return;
    //     }
    //     //clearAllButRoute()
    //     document.body.classList.add('adding-spot')
    //     bar('.topbar.spot.step1')

    //     L.DomEvent.stopPropagation(e)
    // }

    return controlDiv;
  },
});

export default AddSpotButton;
