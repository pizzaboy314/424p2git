var morning = Array(5,13,15,16,17,20,21,23,25,28,30,31,33,36,37,43,44,47,48,49,51,52,53,56,59,61,62,67,72,74,75,81,84,85,86,90,91,94,97,98,100,108,115,130,137,141,156,164,168,173,175,176,181,183,190,192,196,211,255)
var lunch = Array(15,16,21,23,28,30,46,50,54,56,58,66,71,73,74,75,77,80,84,88,91,92,130,137,153,174,175,183,190,192)
var after_work = Array(5,15,17,21,23,28,29,30,31,36,37,44,48,49,51,52,53,54,59,72,75,81,84,86,91,94,97,98,164,166,168,175,183,191,192,195,197)
var evening = Array(13,15,33,37,43,44,48,52,66,75)

imbalance = new L.FeatureGroup();
function showImbalance(timep) {
  removeAllMarkers()
  imbalance.eachLayer(function(marker) {
    imbalance.removeLayer(marker);
  });
  var overloadIcon = L.icon( {
    iconUrl: 'images/overload.png',

    iconSize:     [32, 35], // size of the icon
    shadowSize:   [38, 35], // size of the shadow
    iconAnchor:   [22, 35], // point of the icon which will correspond to marker's location
    shadowAnchor: [4, 34],  // the same for the shadow
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});
  for (i=0; i<timep.length; i++) {
    var latlon = window.stations_latlon.get(timep[i].toString())
    var marker = L.marker([latlon[0],latlon[1]],
      {icon:overloadIcon});
    marker.station_id = timep[i]
    marker.bindPopup('<div id="pin-container"><div class="pin"><div class="pin-name"><span>'+marker.station_id+'</span></div><img src="images/icon-inflow-outflow-pin.png" class="pin-icon"/><div class="pin-inflow highlight"><span>In: '+window.inflow.get(parseInt(marker.station_id))+'</span></div><div class="pin-outflow"><span>Out: '+window.outflow.get(parseInt(marker.station_id))+'</span></div></div></div>');
    imbalance.addLayer(marker);
  }
  imbalance.addTo(map); 
}
