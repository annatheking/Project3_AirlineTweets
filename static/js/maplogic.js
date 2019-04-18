var usCoords = [37.090240,-95.712891];
var mapZoomLevel = 5;

function createMap(tweets) {
  // Adding tile layer
  var streetmap = L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
  attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
  maxZoom: 18,
  id: "mapbox.streets",
  accessToken: "pk.eyJ1IjoiYXJsZW5tYXAiLCJhIjoiY2p0dWxydjRmMWZpcDN5cGVsNXU4aWZzbSJ9.amgRRDDH7ctER8j5VE65Gw"
  });

  // Create a baseMaps object to hold the Street layer
  var baseMaps = {
    "Street Map": streetmap
  };

  // Create an overlayMaps object to hold the bikeStations layer
  var overlayMaps = {
    "Tweets": tweets
  };

  // Create the map object with options
  var map = L.map("map-id", {
    center: usCoords,
    zoom: mapZoomLevel,
    layers: [streetmap, tweets]
  });

  // Create a layer control, pass in the baseMaps and overlayMaps. Add the layer control to the map
  L.control.layers(baseMaps, overlayMaps, {
    collapsed: false
  }).addTo(map);

}

function chooseIcon(sentiment){
  var greenIcon = L.icon({
    iconUrl: '/static/images/leaf-green.png',
    iconSize: [32, 37],
    iconAnchor: [16, 37],
    popupAnchor: [0, -28]
  });
  var redIcon = L.icon({
    iconUrl: '/static/images/leaf-red.png',
    iconSize: [32, 37],
    iconAnchor: [16, 37],
    popupAnchor: [0, -28]
  });
  var orangeIcon = L.icon({
    iconUrl: '/static/images/leaf-orange.png',
    iconSize: [32, 37],
    iconAnchor: [16, 37],
    popupAnchor: [0, -28]
  });

  if(sentiment=='positive')
    return greenIcon;
  else if (sentiment=='neutral')
    return orangeIcon;
  else
    return redIcon
}

/**
 * Create custom marker per tweet sentiment
 */
function createMarkers(response) {
  // Initialize an array to hold bike markers
  var tweets = [];
  // Loop through the stations array
  response.map_data.forEach(tweet => {
    var objtweet = L.marker([tweet.lat, tweet.lng],{icon: chooseIcon(tweet.sentiment)})
      .bindPopup(`<h3>${tweet.airline}</h3><h4>${tweet.sentiment}</h4><h5>${tweet.text}</h5>`);
    tweets.push(objtweet);
  })

  // Create a layer group made from the bike markers array, pass it into the createMap function
  createMap(L.layerGroup(tweets));
}


/**
 * Get the data from the AirlineTwitter database
 */
d3.json("/api/map").then(createMarkers);
