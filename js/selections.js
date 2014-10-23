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
  return url;
}

function selectionUpdate() {
  if (window.selection.length == 0) {
    console.log("hiding selections");
    d3.selectAll(".selection_graph").html(""); 
  } else {
    d3.selectAll(".selection_graph").style("display", "inline");
  
    yearDayUrl = buildUrl('http://trustdarkness.com/py/bikes_out_by_day/');
    ourCsv = d3.text(yearDayUrl)
      .get (function(error, data) {
        yearDayBar(data, "#bikes-per-year-selected", "Date", "Count", "#fdbb84", 200);
    });
  }
  
}

window.selection = new Array;
window.selected_markers = new Array;
