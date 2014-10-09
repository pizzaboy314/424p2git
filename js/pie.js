function renderPieChart(ourData, ourDiv, ourColor)  {               
  d = d3.csv.parseRows(ourData);

  // this is a hack and should be fixed
  data = []
  for (i = 1; i < d.length; i++) {
    data.push({"label":d[i][0], "value":d[i][1]})
  } 

  d3.select(ourDiv).select("svg").remove()

  var canvas = d3.select(ourDiv)
    .append('svg')
    .attr({'width':310,'height':320});

  var colors = [ourColor];
  for (i = 1; i < d.length; i++) {
    ourColor = colorLight(ourColor, .5);
    colors.push(ourColor)
  }
  var colorscale = d3.scale.linear().domain([0,data.length]).range(colors);

  var arc = d3.svg.arc()
    .innerRadius(0)
    .outerRadius(90);

  var arcOver = d3.svg.arc()
    .innerRadius(0)
    .outerRadius(90 + 10);

  var pie = d3.layout.pie()
    .value(function(d){ return d.value; });

  var renderarcs = canvas.append('g')
    .attr('transform','translate(100,100)')
    .selectAll('.arc')
    .data(pie(data))
    .enter()
    .append('g')
    .attr('class',"arc");

  renderarcs.append('path')
    .attr('d',arc)
    .attr('fill',function(d,i){ return colorscale(i); })
    .on("mouseover", function(d) {
      d3.select(this).transition()
      .duration(1000)
      .attr("d", arcOver);
    })
    .on("mouseout", function(d) {
      d3.select(this).transition()
        .duration(1000)
        .attr("d", arc);
    });

    renderarcs.append('text')
//      .style("text-anchor", "middle")
      .style('font-family', 'Helvetica,Arial,sans-serif')
      .style('font-size', '7pt')
//      .attr('transform',function(d) { 
//      var c = arc.centroid(d);
//        console.log(c);
//        return "translate(" + c[0]+15 +"," + c[1]+50 + ")";
//      })
     .attr("text-anchor", function(d) {
     // are we past the center?
       return (d.endAngle + d.startAngle)/2 > Math.PI ?
         "end" : "start";
      })  
      .attr("transform", function(d) {
      var c = arc.centroid(d),
        x = c[0],
        y = c[1],
        // pythagorean theorem for hypotenuse
        h = Math.sqrt(x*x + y*y);
        rad = d.endAngle - d.startAngle
        if (rad < 1.57) {
          cn = 76;
        } else {
          cn = 10;
        }
        console.log(d);
        return "translate(" + (x/h * cn) +  ',' +
                         (y/h * cn) +  ")"; 
      })
      .text(function(d){ 
        return d.data.label+" "+d.value+""; 
      });

}

// Below code borrowed from http://stackoverflow.com/questions/1507931/generate-lighter-darker-color-in-css-using-javascript
function colorLight(hex, lum) {
// // validate hex string
  hex = String(hex).replace(/[^0-9a-f]/gi, '');
  if (hex.length < 6) {
    hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
  }
  lum = lum || 0;
  // convert to decimal and change luminosity
  var rgb = "#", c, i;
  for (i = 0; i < 3; i++) {
    c = parseInt(hex.substr(i*2,2), 16);
    c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
    rgb += ("00"+c).substr(c.length);
  }
  console.log("rbg "+rgb);
  return rgb;
}

