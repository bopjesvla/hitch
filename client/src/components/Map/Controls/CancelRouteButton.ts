import L from 'leaflet';

const CancelRouteButton = L.Control.extend({
  options: {
    position: 'topleft',
  },
  onAdd: () => {
    const controlDiv = L.DomUtil.create('div', 'leaflet-bar clear-none');
    const container = L.DomUtil.create('a', '!w-auto !h-auto px-2', controlDiv);
    container.href = 'javascript:void(0);';
    container.innerHTML = '✖ Cancel Route';

    // container.onclick = function (e) {
    //     clearRoute()
    //     L.DomEvent.stopPropagation(e)
    // }

    return controlDiv;
  },
});

export default CancelRouteButton;
