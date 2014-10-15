function playback(date) {
  url = 'http://trustdarkness.com/py/get_day/'+date
  var i = 0;
    setInterval(function() {
    csv = d3.csv(url)
    .get(function(error,data) {
      dateData = data;
      console.log("our Data: " +data);
        if (dateData[i]) {
          tsa = dateData[i].timestamp.split(" ");
          time = tsa[1];
          hour = time.split(":")[0];
          var tripstring = " "+time+" - From: "+dateData[i].from+" To: "+dateData[i].to;
          console.log("trying to replay trip "+tripstring);
          d3.selectAll(".tripdata")
            .html(" ");
          d3.select("#i"+hour)
            .attr("class", "selected");
          d3.select("#i"+hour).select(".tripdata")
            .html(tripstring);
        }
    }); 
    i++;
    if (i == dateData.length) { return null; };
  }, 100)
 }
