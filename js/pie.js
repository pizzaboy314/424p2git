function renderPieChart(ourData, ourDiv, colorBase)  {               
  d = d3.csv.parseRows(ourData);
  reds = ['rgb(255,245,235)','rgb(254,230,206)','rgb(253,208,162)','rgb(253,174,107)','rgb(253,141,60)','rgb(241,105,19)','rgb(217,72,1)','rgb(140,45,4)']
  blues = ['rgb(247,251,255)','rgb(198,219,239)','rgb(107,174,214)','rgb(33,113,181)']
  greens = ['rgb(229,245,224)','rgb(199,233,192)','rgb(116,196,118)','rgb(65,171,93)']

  switch(colorBase) {
    case "red":
      colors = reds.reverse()
      break;
    case "blue":
      colors = blues.reverse()
      break;
    case "green":
      colors = greens.reverse()
      break;
    default: 
      colors = ['rgb(215,48,39)','rgb(244,109,67)','rgb(253,174,97)','rgb(254,224,139)','rgb(255,255,191)','rgb(217,239,139)','rgb(166,217,106)','rgb(102,189,99)','rgb(26,152,80)']
   }
  // this is a hack and should be fixed
  data = []
  for (i = 1; i < d.length; i++) {
    data.push({"label":d[i][0], "value":d[i][1]})
  } 

  d3.select(ourDiv).select("svg").remove()

  var canvas = d3.select(ourDiv)
    .append('svg')
    .attr({'width':310,'height': 250})
    .style("padding-left", "70px")
    .style("padding-top", "25px");

  var colorscale = d3.scale.linear().domain([0,data.length]).range(colors);

  var arc = d3.svg.arc()
    .innerRadius(0)
    .outerRadius(87);

  var arcOver = d3.svg.arc()
    .innerRadius(0)
    .outerRadius(87 + 10);

  var pie = d3.layout.pie()
    .value(function(d){ return d.value; })
    .sort(null);
 

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
      .style('font-size', '10pt')
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
        if ((rad < 1.57) || ((d.startAngle >1.6) && (d.startAngle < 2) )) {
          cn = 89;
        } else {
          cn = 10;
        }
        //console.log(d);
        return "translate(" + (x/h * cn) +  ',' +
                         (y/h * cn) +  ")"; 
      })
      .text(function(d){ 
        return d.data.label+" "+d.value+""; 
      });

}

