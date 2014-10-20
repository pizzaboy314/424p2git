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

function clearSelection() {
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
