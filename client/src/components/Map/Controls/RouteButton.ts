import L from 'leaflet';

const RouteButton = L.Control.extend({
  options: {
    position: 'topleft',
  },
  onAdd: () => {
    const controlDiv = L.DomUtil.create('div', 'leaflet-bar clear-none');
    const container = L.DomUtil.create('a', '!w-auto !h-auto px-2', controlDiv);
    container.href = 'javascript:void(0);';
    container.innerHTML = '↗️ Plan route';

    // container.onclick = function (e) {
    //     clearAllButRoute()
    //     document.body.classList.add('planning-route')
    //     bar('.topbar.route.step1')
    //     L.DomEvent.stopPropagation(e)
    // }

    return controlDiv;
  },
});

export default RouteButton;
