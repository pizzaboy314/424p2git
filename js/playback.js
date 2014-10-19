function playback(date) {
  d3.select("#playLoading").html("<img src='images/spinner.gif' />");
  url = 'http://trustdarkness.com/py/get_day/'+date
  if (window.genderLimit) {
    url += "?gender="window.genderLimit;
    if (window.usertypeLimit) {
      url += "&subscriber="+window.usertypeLimit;
    }
  } else if (window.usertypeLimit) {
    url += "?subscriber="+window.usertypeLimit;
  }
  csv = d3.csv(url)
  .get(function(error,data) {
    dateData = data;
  })
  var removed = 0;
  var added = 0;
    window.repeat = setInterval(function() {
      if (dateData[window.playbackEvent]) {
        d3.select("#playLoading").html("");
        tsa = dateData[window.playbackEvent].timestamp.split(" ");
        time = tsa[1];
        hour = time.split(":")[0];
        if (window.running.has(dateData[window.playbackEvent].trip_id)) {
          window.running.get(dateData[window.playbackEvent].trip_id).hide();
          window.running.get(
            dateData[window.playbackEvent].trip_id).spliceWaypoints(0,2);
          window.running.delete(dateData[window.playbackEvent].trip_id);
          removed++;
          window.playbackEvent++;
        } else {
	  d3.select("#playLoading").html("");
          var tripstring = " "+time+" - From: "+
            dateData[window.playbackEvent].from+" To: "+dateData[i].to;
          console.log("trying to replay trip "+tripstring);
          d3.selectAll(".tripdata")
            .html(" ");
          d3.select("#day").selectAll(".selected").attr("class", "");
          d3.select("#i"+hour)
            .attr("class", "selected");
          d3.select("#i"+hour).select(".tripdata")
            .html(tripstring);
          var trip = L.Routing.control({ 
            waypoints: [
              L.latLng(dateData[window.playbackEvent].flat,
                dateData[window.playbackEvent].flong),
              L.latLng(dateData[window.playbackEvent].tlat,
                dateData[window.playbackEvent].tlong)
            ],
            fitSelectedRoutes: false
          });
          window.running.set(dateData[window.playbackEvent].trip_id, trip); 
          trip.addTo(map);
          added++;
          window.playbackEvent++;
        }
      }
      if (window.running.size == 0) {
        d3.select("map").selectAll("path").remove()
        d3.select("#day").selectAll("li").attr("class", "");
      } else {
        console.log("window.running.size: "+window.running.size);
      }
    if (window.playbackEvent == dateData.length+1) { 
      console.log("trying to clearInterval"); 
      window.clearInterval(repeat); 
      d3.selectAll(".tripdata").html("");
    };
  }, 400);
}

function sameSrcDst(trip) {
  if (trip.flat == trip.tlat) {
    if (trip.flong == trip.tlong) {
      return true;
    }
  }
  return false;
}

function resetPlayback() {
  d3.select("#playLoading").html("");
  window.playing = false;
  window.started = false;
  window.running = new Map;
  window.playbackEvent = 0;
  window.genderLimit = false;
  clearInterval(window.repeat);
  d3.selectAll(".tripdata").html("");
  d3.select("#day").selectAll("li").attr("class", "");
  d3.select("map").selectAll("path").remove();
  d3.selectAll(".leaflet-marker-pane").selectAll("img").remove();
  d3.selectAll(".leaflet-shadow-pane").selectAll("img").remove();
  d3.select("#playbutton").html("Play");
  $('#radiogender input').removeAttr('checked');
  // Refresh the jQuery UI buttonset.                  
  $( "#radiogender" ).buttonset('refresh');
  $('#radiousertype input').removeAttr('checked');
  // Refresh the jQuery UI buttonset.                  
  $( "#radiousertype" ).buttonset('refresh');
}
