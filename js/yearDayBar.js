
function yearDayBar(csv, display_div, xname, yname, color) {
  var data = d3.csv.parse(csv);
  var valueLabelWidth = 40; // space reserved for value labels (right)
  var barHeight = 8 // height of one bar
  var barLabelWidth = 80// space reserved for bar labels
  var barLabelPadding = 8; // padding between bar and bar labels (left)
  var gridLabelHeight = 40 // space reserved for gridline labels
  var gridChartOffset = 3; // space between start of grid and first bar
  var maxBarWidth = 400 // width of the bar with the max value

  // accessor functions 
  var barLabel = function(d) { return d[xname]; };
  var barValue = function(d) { return parseFloat(d[yname]); };

  // scales
  var yScale = d3.scale.ordinal().domain(d3.range(0, data.length)).rangeBands([0, data.length * barHeight]);
  var y = function(d, i) { return yScale(i); };
  var yText = function(d, i) { return y(d, i) + yScale.rangeBand() / 2; };
  var x = d3.scale.linear().domain([0, d3.max(data, barValue)]).range([0, maxBarWidth]);

  console.log("removing "+display_div);
  d3.select(display_div).select("svg").remove()
  var chart = d3.select(display_div).append("svg")
    .attr('width', maxBarWidth + barLabelWidth + valueLabelWidth)
    .attr('height', gridLabelHeight + gridChartOffset + data.length * barHeight)
    //.style('background-color', '#aeaeae')
    .style('margin-top', '5px')
    .style('padding-bottom', '10px')
    .style('padding-right', '10px')

  // grid line labels
  var gridContainer = chart.append('g')
    .attr('transform', 'translate(' + barLabelWidth + ',' + gridLabelHeight + ')'); 

  gridContainer.selectAll("text").data(x.ticks(10)).enter().append("text")
    .attr("x", x)
    .attr("dy", -3)
    .attr("text-anchor", "middle")
    //.text(String)
    .style('font-family', 'Helvetica,Arial,sans-serif')
    .style('font-size', '7pt');

  // vertical grid lines
  gridContainer.selectAll("line").data(x.ticks(10)).enter().append("line")
    .attr("x1", x)
    .attr("x2", x)
    .attr("y1", 0)
    .attr("y2", yScale.rangeExtent()[1] + gridChartOffset)
    .style("stroke", "#ccc");

  // bar labels
  var labelsContainer = chart.append('g')
    .attr('transform', 'translate(' + (barLabelWidth - barLabelPadding) + ',' + (gridLabelHeight + gridChartOffset) + ')'); 
  labelsContainer.selectAll('text').data(data).enter().append('text')
    .attr('y', yText)
    .attr('stroke', 'none')
    .attr('fill', '#494949')
    .style('font-family', 'Helvetica,Arial,sans-serif')
    .style('font-size', '7pt')
    .attr("dy", ".35em") // vertical-align: middle
    .attr('text-anchor', 'end')
    .text(barLabel);

  // bars
  var barsContainer = chart.append('g')
    .attr('transform', 'translate(' + barLabelWidth + ',' + (gridLabelHeight + gridChartOffset) + ')'); 
  barsContainer.selectAll("rect").data(data).enter().append("rect")
    .attr('y', y)
    .attr('height', yScale.rangeBand())
    .attr('width', function(d) { return x(barValue(d)); })
    .attr('stroke', 'white')
    .attr('fill', color);

  // bar value labels
  barsContainer.selectAll("text").data(data).enter().append("text")
    .attr("x", function(d) { return x(barValue(d)); })
    .attr("y", yText)
    .attr("dx", 3) // padding-left
    .attr("dy", ".35em") //contentDival-align: middle
    .attr("text-anchor", "start") // text-align: right
    .style('font-family', 'Helvetica,Arial,sans-serif')
    .style('font-size', '7pt')
    .attr("fill", "#494949")
    .attr("stroke", "none")
    .text(function(d) { return d3.round(barValue(d), 2); });

  // start line
  barsContainer.append("line")
    .attr("y1", -gridChartOffset)
    .attr("y2", yScale.rangeExtent()[1] + gridChartOffset)
    .style("stroke", "#000");

  barsContainer.append("text")
    .attr("x", 0)
    .attr("y", -10)
    .style("text-anchor", "left")
    .style('font-family', 'Helvetica,Arial,sans-serif')
    .style('font-size', '10pt')
    .text("Number of bikes out by day of the year");
}
