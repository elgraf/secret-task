$(document).ready(function() {
	//Chart.scaleService.registerScaleType('modifier', MyScale, defaultConfigObject);
	var date_unit = function(){
		if ((end - begin)/86400000 > 90) { // days
			return 'month';
		} else {
			return 'day'
		}
	}
	var priceChart = new Chart(document.getElementById("priceChart"), {
		type: 'line',
		data: {
			labels: [],
			datasets: [{
				lineTension: 0,           
				data: [],
				label: "Price",
				borderWidth: 2,
				borderColor: "#3e95cd",
				fill: true,
				pointRadius: 3
			},
			{
				lineTension: 0,           
				data: [],
				label: "Category modifier",
				showLine: true,
				borderWidth: 2,
				borderColor: "red",
				fill: false,
				pointRadius: 3
			},
			{
				lineTension: 0,           
				data: [],
				label: "Product modifier",
				showLine: true,
				borderWidth: 2,
				borderColor: "orange",
				fill: false,
				pointRadius: 3
			}]
		},
		options: {
			tooltips: {
				mode: 'index',
				intersect: false,
			},
			scales: {
				xAxes: [{
					type: 'time',
					time: {
						parser: 'YYYY-MM-DD',
						unit: date_unit(),
						displayFormats: {
							day: 'DD-MM',
							month: 'MM-YY',
						},
						min: begin,
						max: end
					},
					ticks: {
						source: 'data',
					}
				}]
			},
			legend: {
				display: false
			},
			animation: {
				duration: 0,
			},
			hover: {
				animationDuration: 0,
			},
			responsiveAnimationDuration: 0
		},
		plugins: [{
			beforeInit: function(chart) {
				var i = 0;
				dumped_data.forEach(function(dumped){
					var data = JSON.parse(dumped).chart;
					data.forEach(function(point) {
						var _label = moment(point.date).format('YYYY-MM-DD');
						var _modifier = point.m;
						chart.data.datasets[i].data.push({y:_modifier,
							x:_label});

					});
					i++;
				})
			}
		}]
	});
	$( function() {
		var prev_end = 2200;
		var prev_begin = 0
	  $( "#slider-range" ).slider({
		range: true,
		min: 0,
		max: 2200,
		values: [ 0, 2000 ],
		slide: function( event, ui ) {
			$( "#amount" ).val( begin.add(ui.values[0] - prev_begin, 'd').format(
				'YYYY-MM-DD') + " - " + end.add(
				ui.values[1] - prev_end, 'd').format('YYYY-MM-DD'));

			priceChart.options.scales.xAxes[0].time.unit = date_unit();
			priceChart.update()
			prev_end = ui.values[1];
			prev_begin =  ui.values[0];
		}
	  });
	  $( "#amount" ).val( begin.format('YYYY-MM-DD') + " - " + end.format(
		  'YYYY-MM-DD'));
	} );

});
