import L from 'leaflet';
import { useUiStore } from '@/stores/ui';

const MenuButton = L.Control.extend({
  options: {
    position: 'topleft',
  },
  onAdd: () => {
    const controlDiv = L.DomUtil.create('div', 'leaflet-bar horizontal-button');
    const container = L.DomUtil.create('a', '', controlDiv);
    container.href = 'javascript:void(0);';
    container.innerHTML = '☰';

    container.onclick = function (e) {
      const uiStore = useUiStore();
      uiStore.toggleSidebar('Menu');
      L.DomEvent.stopPropagation(e);
    };

    return controlDiv;
  },
});

export default MenuButton;
