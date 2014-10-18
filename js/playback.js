function playback(date) {
  url = 'http://trustdarkness.com/py/get_day/'+date
  csv = d3.csv(url)
  .get(function(error,data) {
    dateData = data;
  })
  var i = 0;
  var removed = 0;
  var added = 0;
    var repeat = setInterval(function() {
      if (dateData[i]) {
        tsa = dateData[i].timestamp.split(" ");
        time = tsa[1];
        hour = time.split(":")[0];
        if (window.running.has(dateData[i].trip_id)) {
          console.log("trying to remove trip #"+dateData[i].trip_id);
          window.running.get(dateData[i].trip_id).hide();
          window.running.get(dateData[i].trip_id).spliceWaypoints(0,2);
          window.running.delete(dateData[i].trip_id);
          d3.select("#i"+hour+" #i"+hour-1)
            .attr("class", "");
          removed++;
          i++;
        } else {
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
          added++;
          i++;
        }
      }
      if (window.running.size == 0) {
        d3.selectAll("path").remove()
        d3.select("#day").selectAll("li").attr("class", "");
      } else {
        console.log("window.running.size: "+window.running.size);
      }
    console.log("final playback: touched: "+i+" added: "+added+" removed: "+removed);
    if (i == dateData.length) { console.log("trying to clearInterval"); window.clearInterval(repeat); };
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
