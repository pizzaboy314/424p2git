function renderPieChart(ourData, ourDiv, ourColor)  {               
  d = d3.csv.parseRows(ourData);

  data = [{"label":d[1][0], "value":d[1][1]},
          {"label":d[2][0], "value":d[2][1]}]

  d3.select(ourDiv).select("svg").remove()

  var canvas = d3.select(ourDiv)
    .append('svg')
    .attr({'width':320,'height':200});

  var colors = [ourColor, colorLight(ourColor, .5)];
  var colorscale = d3.scale.linear().domain([0,data.length]).range(colors);

  var arc = d3.svg.arc()
    .innerRadius(0)
    .outerRadius(80);

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
      .style("text-anchor", "middle")
      .style('font-family', 'Helvetica,Arial,sans-serif')
      .style('font-size', '8pt')
      .attr('transform',function(d) { 
      var c = arc.centroid(d);
        console.log(c);
        return "translate(" + c[0] +"," + c[1]+ ")";
      })
      .text(function(d){ 
        console.log(d);
        return d.data.label+" "+d.value+"%"; 
      });

}
