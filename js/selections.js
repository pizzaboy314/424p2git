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
}

function removeStationsFromSelection(stations) {
    for (i=0; i<stations.length; i++) {
      window.selection.pop(stations[i])
    }
}

function removeNeighborhoodFromSelection(neighborhood_slug) {
  stations = window.neighborhood_map.get(neighborhood_slug)
  if (stations) {
    for (i=0; i<stations.length; i++) {
      window.selection.pop(stations[i])
    }
  }
  console.log("selection now has "+window.selection.length+" items");
}

function doTheSelect(e) {
  var ourMarker = this;
  ourMarker.oldIcon = ourMarker._icon;
  ourMarker.setIcon(defaultIcon);
  window.tmp3 = ourMarker;
  window.selection.push(this.station_id);
  window.selected_markers.push(ourMarker);
}

function clearSelection() {
  window.selection = new Array;
  for (i=0; i<window.selected_markers; i++) {
    window.selected_markers.setIcon(window.selected_markers.oldIcon);
  }
  window.selected_markers = new Array;
}

function splitMap(map) {
  window.one = new Array;
  window.two = new Array;
  map.forEach(function(value, key) {
    window.one.push(key);
    window.two.push(value);
  })
}

window.selection = new Array;
window.selected_markers = new Array;
