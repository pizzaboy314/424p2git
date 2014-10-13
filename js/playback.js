function playback(date) {
  var ourData;
  url = 'http://trustdarkness.com/py/get_day/'+date
  csv = d3.csv(url);
    .get(function(error,data) {
      ourData = data;
      console.log("our Data: " +ourData);
  })
}
