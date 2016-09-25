
function range(start, count) {
    return Array.apply(0, Array(count))
        .map(function (element, index) { 
            return index + start;  
        });
}

function draw_timeseries(timeseries, name_1, name_2){
    console.log(name_1)
    //console.log(timeseries['name_2'])
    $('#timeseries_graph').highcharts({
        title: {
            text: ' ',
            x: -20 //center
        },
        subtitle: {
            text: ' ',
            x: -20
        },
        xAxis: {
            categories: range(1994, 21)
        },
        yAxis: {
            title: {
                text: '# per 10000'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            enabled: false
        },
        legend: {
            layout: 'horizontal',
            align: 'center',
            verticalAlign: 'bottom',
            borderWidth: 0,
            floating: false
        },
        series: [{
            name: name_1,
            data: timeseries['name_1']
        }, {
            name: name_2,
            data: timeseries['name_2']
        }]
    });
}