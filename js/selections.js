function addStationsToSelection(stations) {
}

function addNeighborhoodToSelection(neighborhood_slug) {
  stations = window.neighborhood_map.get(neighborhood_slug)
  if (stations) {
    for (i=0; i<stations.length; i++) {
      window.selection.push(stations[i])
    }
  }
  console.log("selection now has "+window.selection.length+" items");
  selectionUpdate();
}

function removeStationsFromSelection(stations) {
    for (i=0; i<stations.length; i++) {
      window.selection.pop(stations[i])
    }
    selectionUpdate();

}

function removeNeighborhoodFromSelection(neighborhood_slug) {
  stations = window.neighborhood_map.get(neighborhood_slug)
  if (stations) {
    for (i=0; i<stations.length; i++) {
      window.selection.pop(stations[i])
    }
  }
  console.log("selection now has "+window.selection.length+" items");
  selectionUpdate();
}

function doTheSelect(e) {
  var ourMarker = this;
   for (i=0; i< window.selected_markers.length; i++) { 
     if (window.selected_markers[i].station_id == ourMarker.station_id) {
       console.log("trying to remove on dblclick");
       window.selected_markers.pop(ourMarker);
       ourMarker.setIcon(ourMarker.oldIcon);
       window.selection.pop(ourMarker.station_id);
       selectionUpdate();
      }
    }
    ourMarker.oldIcon = ourMarker._icon;
    ourMarker.setIcon(defaultIcon);
    window.tmp3 = ourMarker;
    if (!ourMarker.station_id) {
      alert("station_id missing");
    }
    window.selection.push(ourMarker.station_id);
    window.selected_markers.push(ourMarker);
    selectionUpdate();
}

function clearSelection() {
  window.selection = new Array;
  for (i=0; i<window.selected_markers; i++) {
    window.selected_markers.setIcon(window.selected_markers.oldIcon);
  }
  window.selected_markers = new Array;
  selectionUpdate();
}

function splitMap(map) {
  window.one = new Array;
  window.two = new Array;
  map.forEach(function(value, key) {
    window.one.push(key);
    window.two.push(value);
  })
}

function buildUrl(url) {
  if (window.genderLimit) {
    url += "?gender="+window.genderLimit;
    if (window.usertypeLimit) {
      url += "&subscriber="+window.usertypeLimit;
      if (window.selection.length > 0) {
        url +="&stations="+window.selection;
        if (window.ageLimit) {
          url +="&age="+window.ageLimit;
          if (window.dateLimit) {
            url += "&date="+window.dateLimit;
          }
        }
      }
    }
  } else if (window.usertypeLimit) {
    url += "?subscriber="+window.usertypeLimit;
    if (window.selection.length > 0) {
      url +="&stations="+window.selection;
      if (window.ageLimit) {
        url +="&age="+window.ageLimit;
        if (window.dateLimit) {
          url+="&date="+window.dateLimit;
        }
      }
    }
  } else if (window.selection.length > 0) {
     url += "?stations="+window.selection;
     if (window.ageLimit) {
        url +="&age="+window.ageLimit;
        if (window.dateLimit) {
          url += "&date="+window.dateLimit;
        }
     }
  } else if (window.ageLimit) {
    url +="?age="+window.ageLimit;
    if (window.dateLimit) {
      url+="&date="+window.dateLimit;
    }
  } else if (window.dateLimit) {
    url +="?date="+window.dateLimit;
  }
  return url;
}

function selectionUpdate() {
  if (window.selection.length == 0) {
    console.log("hiding selections");
    d3.selectAll(".selection_graph").html(""); 
  } else {
    d3.selectAll(".selection_graph").style("display", "inline");
    d3.selectAll(".selection_graph").html('<div class="inline" id="facebookG"><div id="blockG_1" class="facebook_blockG"></div><div id="blockG_2" class="facebook_blockG"></div><div id="blockG_3" class="facebook_blockG"></div>').style("float", "right").style("padding-right", "175px").style("padding-top", "30px"); 
    yearDayUrl = buildUrl('http://trustdarkness.com/py/bikes_out_by_day/');
    ourCsv = d3.text(yearDayUrl)
      .get (function(error, data) {
        yearDayBar(data, "#bikes-per-year-selected", "Date", "Count", "#fdbb84", 200);
        d3.select("#bikes-per-year-selected")
          .style("padding-right", "20px").style("padding-top", "0px")
          .select("#facebookG").remove();
    });
    ageUrl = buildUrl('http://trustdarkness.com/py/age/');
    ourCsv = d3.text(ageUrl)
      .get (function(error, data) {
         renderPieChart(data, "#age-selected", "#fdbb84");
    });
    genderUrl = buildUrl('http://trustdarkness.com/py/gender/');
    ourCsv = d3.text(genderUrl)
      .get (function(error, data) {
        renderPieChart(data, "#gender-selected", "blue");
    });
    usertypeUrl = buildUrl('http://trustdarkness.com/py/usertype/');
    ourCsv = d3.text(usertypeUrl)
      .get(function(error, data) {
        renderPieChart(data, "#type-selected", "green");
    });

    hoursUrl = buildUrl('http://trustdarkness.com/py/hour_of_day/');
    hourOfDayBar(hoursUrl, "#chartHourOfDay-selected");

    daysUrl = buildUrl('http://trustdarkness.com/py/day_of_week/');
    dayOfWeekBar(daysUrl, "#chartDayOfWeek-selected");
 
    distanceUrl = buildUrl('http://trustdarkness.com/py/distance_dist/');
    distancesOverallBar(distanceUrl, "#chartDistancesOverall-selected");

    timesUrl = buildUrl('http://trustdarkness.com/py/time_dist/');
    timesOverallBar(timesUrl, "#chartTimesOverall-selected");
    d3.selectAll(".selection_graph")
      .style("background-color", "rgba(222,235,247,1)")
      .style("border", "2px #ff7800");

  }
  
}

function resetMap() {
  clearSelection();
  if (window.playing) {
    resetPlayback();
  }
  removeAllMarkers();
  repopulate();
}

window.selection = new Array;
window.selected_markers = new Array;
