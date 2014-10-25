function dayOfWeekBar(url, display_div) {
	var margin = {top: 20, right: 30, bottom: 30, left: 50},
		width = 420 - margin.left - margin.right,
		height = 250 - margin.top - margin.bottom;

	var x = d3.scale.ordinal()
		.rangeRoundBands([0, width], .1);

	var y = d3.scale.linear()
		.range([height, 0]);

	var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom");

	var yAxis = d3.svg.axis()
		.scale(y)
		.orient("left");
		
	d3.json(url, function(error, data) {
          d3.select(display_div).select("svg").remove()
        if (display_div.indexOf("selected") > 0) {
          d3.select(display_div).html(" ")
            .style("padding-right", "0")
            .style("padding-top", "0");
        }

          var chart = d3.select(display_div).append("svg")
                .attr("class", "chartOverview")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	  x.domain(data.map(function(d) { return d.range; }));
	  y.domain([0, d3.max(data, function(d) { return +d.frequency; })]);

	  chart.append("g")
		  .attr("class", "xaxis")
		  .attr("transform", "translate(0," + height + ")")
		  .call(xAxis);

	  chart.append("g")
		  .attr("class", "yaxis")
		  .call(yAxis);

	  chart.selectAll(".bar")
		  .data(data)
		.enter().append("rect")
		  .attr("class", "bar")
		  .attr("x", function(d) { return x(d.range); })
		  .attr("y", function(d) { return y(d.frequency); })
		  .attr("height", function(d) { return height - y(+d.frequency); })
		  .attr("width", x.rangeBand()-8);
	});

}
