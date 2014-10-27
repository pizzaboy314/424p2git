function playback(date) {
  window.dateLimit = date;
  selectionUpdate();
  d3.select("#playLoading").html("<img src='images/spinner.gif' />");
  url = 'http://trustdarkness.com/py/get_day/'+date
  if (window.genderLimit) {
    url += "?gender="+window.genderLimit;
    if (window.usertypeLimit) {
      url += "&subscriber="+window.usertypeLimit;
      if (window.selection.length > 0) {
        url +="&stations="+window.selection;
        if (window.ageLimit) {
          url +="&age="+window.ageLimit;
        }
      }
    }
  } else if (window.usertypeLimit) {
    url += "?subscriber="+window.usertypeLimit;
    if (window.selection.length > 0) {
      url +="&stations="+window.selection;
      if (window.ageLimit) {
        url +="&age="+window.ageLimit;
      }
    }
  } else if (window.selection.length > 0) {
     url += "?stations="+window.selection;
     if (window.ageLimit) {
        url +="&age="+window.ageLimit;
     }
  } else if (window.ageLimit) {
    url +="?age="+window.ageLimit;
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
            dateData[window.playbackEvent].from+" To: "+dateData[window.playbackEvent].to;
          console.log("trying to replay trip "+tripstring);
          d3.selectAll(".tripdata")
            .html(" ");
          d3.select("#day").selectAll(".selected").attr("class", "");
          d3.select("#i"+hour)
            .attr("class", "selected");
          wchange_hours = Array(0, 6, 10, 12, 14, 17, 19, 22);
            console.log("Yay!");
            d3.csv("http://trustdarkness.com/py/weather/"+date+"/"+hour)
              .get(function(error, data) {
                wicon = data[0].icon;
                temp_f = data[0].temp;
                d3.select('#temp').html(temp_f+'&deg;');
                d3.select('#date').html(moment(date).format('MMMM Do YYYY'));
                d3.select('#wicon').attr('src', 'http://icons.wxug.com/i/c/i/'+wicon+'.gif');
            });
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
          if (window.running.size == 0) {
            d3.select("map").selectAll("path").remove()
            d3.select("#day").selectAll("li").attr("class", "");
          } else {
            console.log("window.running.size: "+window.running.size);
          }
            window.playbackEvent++;
          }
          if (window.playbackEvent == dateData.length) { 
            console.log("trying to clearInterval"); 
            window.clearInterval(repeat); 
            d3.selectAll(".tripdata").html("");
            resetPlayback();
          };
      } else {
        d3.select("#playbackError").html("No data was found for your request.")
        d3.select("#playLoading").html("");
      }
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
  window.dateLimit = false;
  window.running = new Map;
  window.playbackEvent = 0;
  window.genderLimit = false;
  clearInterval(window.repeat);
  d3.selectAll(".tripdata").html("");
         $.ajax(
           { url :
             "http://api.wunderground.com/api/9d7e28be82bf1469/geolookup/conditions/q/IL/Chicago.json",
             dataType : "jsonp",
             success : function(parsed_json) {
               var location = parsed_json['location']['city'];
               var temp_f = parsed_json['current_observation']['temp_f'];
               var wicon = parsed_json['current_observation']['icon'];
               d3.select('#temp').html(temp_f+'&deg;');
               d3.select('#date').html(moment().format('MMMM Do YYYY'));
               d3.select('#wicon').attr('src', 'http://icons.wxug.com/i/c/i/'+wicon+'.gif');
             }
           });
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
  d3.select("#playbackError").html(" ");
  d3.select(".leaflet-overlay-pane").selectAll("g").selectAll(".leaflet-clickable").remove();
         $.ajax(
           { url :
             "http://api.wunderground.com/api/9d7e28be82bf1469/geolookup/conditions/q/IL/Chicago.json",
             dataType : "jsonp",
             success : function(parsed_json) {
               var location = parsed_json['location']['city'];
               var temp_f = parsed_json['current_observation']['temp_f'];
               var wicon = parsed_json['current_observation']['icon'];
               d3.select('#temp').html(temp_f+'&deg;');
               d3.select('#date').html(moment().format('MMMM Do YYYY'));
               d3.select('#wicon').attr('src', 'http://icons.wxug.com/i/c/i/'+wicon+'.gif');
             }
           });

  clearSelection();
}
