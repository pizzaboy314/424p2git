function playback(date) {
  url = 'http://trustdarkness.com/py/get_day/'+date
  csv = d3.csv(url)
  .get(function(error,data) {
    dateData = data;
  })
  var i = 0;
    setInterval(function() {
      if (dateData[i]) {
        if (window.running.has(dateData[i].trip_id)) {
          console.log("trying to remove trip #"+dateData[i].trip_id);
          window.running.get(dateData[i].trip_id).hide();
          window.running.get(dateData[i].trip_id).spliceWaypoints(0,2);
          //map.removeLayer(window.running.get(dateData[i].trip_id).getPlan());
          window.running.delete(dateData[i].trip_id);
          i++;
        } else {
          tsa = dateData[i].timestamp.split(" ");
          time = tsa[1];
          hour = time.split(":")[0];
          var tripstring = " "+time+" - From: "+dateData[i].from+" To: "+dateData[i].to;
          console.log("trying to replay trip "+tripstring);
          d3.selectAll(".tripdata")
            .html(" ");
          d3.select("#i"+hour)
            .attr("class", "selected");
          d3.select("#i"+hour).select(".tripdata")
            .html(tripstring);
          var trip = L.Routing.control({ 
            waypoints: [
              L.latLng(dateData[i].flat,dateData[i].flong),
              L.latLng(dateData[i].tlat,dateData[i].tlong)
            ],
            fitSelectedRoutes: false
          });
          window.running.set(dateData[i].trip_id, trip); 
          //L.Routing.line(trip, { styles: { color: "blue" } } );
          trip.addTo(map);
          i++;
        }
      }
      if (window.running.size == 0) {
        d3.selectAll("path").remove()
      }
    if (i == dateData.length-1) { clearInterval(); };
  }, 300);
}

function sameSrcDst(trip) {
  if (trip.flat == trip.tlat) {
    if (trip.flong == trip.tlong) {
      return true;
    }
  }
  return false;
}
