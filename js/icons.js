        // setup heatmap icons
        var iS = [13, 20]; // size of the icon
        var sS = [10, 16]; // size of the shadow
        var iA = [13, 20]; // point of the icon which will correspond to marker's location
        var sA = [5, 13];  // the same for the shadow
        var pA =  [-1, -20]; // point from which the popup should open relative to the iconAnchor
        var i1 = L.icon({ 
          iconUrl: 'images/divy-0.png',
          shadowUrl: 'images/marker-shadow.png',
          iconSize:     iS, // size of the icon
          shadowSize:   sS, // size of the shadow
          iconAnchor:   iA, // point of the icon which will correspond to marker's location
          shadowAnchor: sA,  // the same for the shadow
          popupAnchor:  pA // point from which the popup should open relative to the iconAnchor
        })
        var i2 = L.icon({ 
          iconUrl: 'images/divy-1.png',
          shadowUrl: 'images/marker-shadow.png',
          iconSize:     iS, // size of the icon
          shadowSize:   sS, // size of the shadow
          iconAnchor:   iA, // point of the icon which will correspond to marker's location
          shadowAnchor: sA,  // the same for the shadow
          popupAnchor:  pA // point from which the popup should open relative to the iconAnchor

        })
        var i3 = L.icon({ 
          iconUrl: 'images/divy-2.png',
          shadowUrl: 'images/marker-shadow.png',          
	  iconSize:     iS, // size of the icon
          shadowSize:   sS, // size of the shadow
          iconAnchor:   iA, // point of the icon which will correspond to marker's location
          shadowAnchor: sA,  // the same for the shadow
          popupAnchor:  pA // point from which the popup should open relative to the iconAnchor
        })
        var i4 = L.icon({ 
          iconUrl: 'images/divy-3.png',
          shadowUrl: 'images/marker-shadow.png',
          iconSize:     iS, // size of the icon
          shadowSize:   sS, // size of the shadow
          iconAnchor:   iA, // point of the icon which will correspond to marker's location
          shadowAnchor: sA,  // the same for the shadow
          popupAnchor:  pA // point from which the popup should open relative to the iconAnchor

        })
        var i5 = L.icon({ 
          iconUrl: 'images/divy-4.png',
          shadowUrl: 'images/marker-shadow.png',
          iconSize:     iS, // size of the icon
          shadowSize:   sS, // size of the shadow
          iconAnchor:   iA, // point of the icon which will correspond to marker's location
          shadowAnchor: sA,  // the same for the shadow
          popupAnchor:  pA // point from which the popup should open relative to the iconAnchor

        })
        var i6 = L.icon({ 
          iconUrl: 'images/divy-5.png',
          shadowUrl: 'images/marker-shadow.png',
          iconSize:     iS, // size of the icon
          shadowSize:   sS, // size of the shadow
          iconAnchor:   iA, // point of the icon which will correspond to marker's location
          shadowAnchor: sA,  // the same for the shadow
          popupAnchor:  pA // point from which the popup should open relative to the iconAnchor

        })
        var i7 = L.icon({ 
          iconUrl: 'images/divy-6.png',
          shadowUrl: 'images/marker-shadow.png',
          iconSize:     iS, // size of the icon
          shadowSize:   sS, // size of the shadow
          iconAnchor:   iA, // point of the icon which will correspond to marker's location
          shadowAnchor: sA,  // the same for the shadow
          popupAnchor:  pA // point from which the popup should open relative to the iconAnchor

        })

var defaultIcon = L.icon({
  iconUrl: 'images/marker-icon.png',
  shadowUrl: 'images/marker-shadow.png',
    iconSize:     [38, 65], // size of the icon
    shadowSize:   [50, 34], // size of the shadow
    iconAnchor:   [22, 64], // point of the icon which will correspond to marker's location
    shadowAnchor: [4, 62],  // the same for the shadow
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});

var inDestIcon = L.icon({
  iconUrl: 'images/indest.png',
  shadowUrl: 'images/marker-shadow.png',
    iconSize:     iS, // size of the icon
    shadowSize:   sS, // size of the shadow
    iconAnchor:   iA, // point of the icon which will correspond to marker's location
    shadowAnchor: sA,  // the same for the shadow
    popupAnchor:  pA // point from which the popup should open relative to the iconAnchor

});

var inSrcIcon = L.icon({
  iconUrl: 'images/divvy-up.png',
  shadowUrl: 'images/marker-shadow.png',
    iconSize:     [35,35], // size of the icon
    shadowSize:   sS, // size of the shadow
    iconAnchor:   [10,10], // point of the icon which will correspond to marker's location
    shadowAnchor: sA,  // the same for the shadow
    popupAnchor:  pA // point from which the popup should open relative to the iconAnchor

});

var outSrcIcon = L.icon({
  iconUrl: 'images/outsrc.png',
  shadowUrl: 'images/marker-shadow.png',
    iconSize:     iS, // size of the icon
    shadowSize:   sS, // size of the shadow
    iconAnchor:   iA, // point of the icon which will correspond to marker's location
    shadowAnchor: sA,  // the same for the shadow
    popupAnchor:  pA // point from which the popup should open relative to the iconAnchor
});

var outDestIcon = L.icon({
  iconUrl: 'images/divvy-down.png',
  shadowUrl: 'images/marker-shadow.png',
    iconSize:     [35,35], // size of the icon
    shadowSize:   sS, // size of the shadow
    iconAnchor:   [10,10], // point of the icon which will correspond to marker's location
    shadowAnchor: sA,  // the same for the shadow
    popupAnchor:  pA // point from which the popup should open relative to the iconAnchor

});
