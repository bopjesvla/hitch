import L from 'leaflet';

const RouteViewButton = L.Control.extend({
  options: {
    position: 'topleft',
  },
  onAdd: () => {
    const controlDiv = L.DomUtil.create('div', 'leaflet-bar clear-none');
    const container = L.DomUtil.create('a', '!w-auto !h-auto px-2', controlDiv);
    container.href = 'javascript:void(0);';
    container.innerHTML = "<span class='route-view-toggle'></span> Route view";

    // container.onclick = function (e) {
    //     document.body.classList.toggle('directions')
    //     L.DomEvent.stopPropagation(e)
    // }

    return controlDiv;
  },
});

export default RouteViewButton;
