var AddHeatmapInfoButton = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-bar horizontal-button heatmap-info');
        var container = L.DomUtil.create('a', '', controlDiv);
        container.href = "javascript:void(0);";
        container.innerHTML = "\u2139 What can I see here?";

        container.onclick = function (e) {
            clearAllButRoute()
            if (document.body.classList.contains('heatmap-info'))
                bar()
            else
                bar('.sidebar.heatmap-info')
            document.body.classList.toggle('heatmap-info')
            L.DomEvent.stopPropagation(e)
        }

        return controlDiv;
    }
});

map.addControl(new AddHeatmapInfoButton());