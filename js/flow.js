function totalInflow(station_id) {
  console.log("loading "+station_id);
  url = 'http://trustdarkness.com/py/inflow/'+station_id
  d3.csv(url)
    .get(function(error, data) {
      count = 0
      for (i=0; i<data.length; i++) { 
        count += parseInt(data[i].count);
      }
      window.total_inflow.set(station_id, count);
    });
}


function drawInflow(station_id) {
  station_id = station_id.toString();
  removeAllMarkers();
  if (map.hasLayer(window.inflowTrips)) {
    map.removeLayer(window.inflowTrips);
  }
  window.inflowTrips = new L.FeatureGroup();
  url = 'http://trustdarkness.com/py/inflow/'+station_id
  slatlon = stations_latlon.get(station_id);
  d3.csv(url)
      .get(function(error, data) {
      count = 0
      for (i=0; i<data.length; i++) {
        dlatlon = stations_latlon.get(data[i].from_station);
        var trip = L.Routing.control({
          plan: L.Routing.plan([
              L.latLng(slatlon[0], slatlon[1]),
              L.latLng(dlatlon[0], dlatlon[1])
          ], 
          { waypointIcon: function(j) {
            if (j== 0) {
              return inSrcIcon;
            } else {
              return inDestIcon;
            }
          }
          }), 
          lineOptions: {
            styles: [
            {color: 'black', opacity: 0, weight: 0},
            {color: 'blue', opacity: 0, weight: 0},
            {color: '#EE513F', opacity: 1, weight: data[i].count/8}
            ]
           },
           fitSelectedRoutes: false
         });
        window.inflowTrips.addLayer(trip);
      }
    });
    window.inflowTrips.addTo(map);
}

function drawOutflow(station_id) {
  station_id = station_id.toString();
  removeAllMarkers();
  if (map.hasLayer(window.outflowTrips)) {
    map.removeLayer(window.outflowTrips);
  }
  window.outflowTrips = new L.FeatureGroup();
  url = 'http://trustdarkness.com/py/outflow/'+station_id
  slatlon = stations_latlon.get(station_id);
  d3.csv(url)
     .get(function(error, data) {
      count = 0
      for (i=0; i<data.length; i++) {
        dlatlon = stations_latlon.get(data[i].to_station);
        var trip = L.Routing.control({
          plan: L.Routing.plan([
              L.latLng(dlatlon[0], dlatlon[1]),
              L.latLng(slatlon[0], slatlon[1])
          ],
          { waypointIcon: function(j) {
            if (j == 0) {
              return outSrcIcon;
            } else {
              return outDestIcon;
            }
           
          }
          }),           
          lineOptions: {
            styles: [
            {color: 'black', opacity: 0, weight: 0},
            {color: 'blue', opacity: 0, weight: 0},
            {color: '#EE513F', opacity: 1, weight: data[i].count/8}
            ]
           },
           fitSelectedRoutes: false
         });
        window.outflowTrips.addLayer(trip);
      }
    });
    window.outflowTrips.addTo(map);
}

function showFlow(timep, date) {
  removeAllMarkers();
  if (!date) {
    alert("Please select a date first");
  }
  url = "http://trustdarkness.com/py/get_"+timep+"_trips/"+date;
  window.overallFlow = new L.FeatureGroup()
  d3.csv(url)
     .get(function(error, data) {
      count = 0
      for (i=0; i<data.length; i++) {
        slatlon = stations_latlon.get(data[i].from_station_id);
        dlatlon = stations_latlon.get(data[i].to_station_id);
        var trip = L.Routing.control({
          plan: L.Routing.plan([
              L.latLng(dlatlon[0], dlatlon[1]),
              L.latLng(slatlon[0], slatlon[1])
          ],
          { waypointIcon: i5 } 
          ),
          lineOptions: {
            styles: [
            {color: 'black', opacity: 0, weight: 0},
            {color: 'blue', opacity: 0, weight: 0},
            {color: 'steelblue', opacity: 1, weight: data[i].count/4}
            ]
           },
           fitSelectedRoutes: false
         });
        window.overallFlow.addLayer(trip);
      }
    });
  window.overallFlow.addTo(map);
}
