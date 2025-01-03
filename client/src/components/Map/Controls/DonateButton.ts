import L from 'leaflet';

const DonateButton = L.Control.extend({
  options: {
    position: 'bottomright',
  },
  onAdd: () => {
    const controlDiv = L.DomUtil.create('div', 'donate-button');
    controlDiv.innerHTML =
      '<a href="https://en.liberapay.com/Bob./donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a>';

    return controlDiv;
  },
});

export default DonateButton;
