
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
        chart: {
            backgroundColor:'#FEEED5',
            style: {
                fontFamily: "'Josefin Sans', sans-serif",
                color: "#1C4977"
            },
        },
        title: {
            text: ' ',
            x: -20 //center
        },
        subtitle: {
            text: ' ',
            x: -20
        },
        xAxis: {
            categories: range(1994, 21),
            lineColor: "#1C4977",
            tickColor: "#1C4977",
            labels: {
                style: {
                    color: "#1C4977",
                    font: "'Josefin Sans', sans-serif",
                }
            },
        },
        yAxis: {
            title: {
                text: '# per 10000'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#1C4977'
            }],
            gridLineColor:'#1C4977',
            lineColor: "#1C4977",
            tickColor: "#1C4977",
            labels: {
                style: {
                    color: "#1C4977",
                    font: "'Josefin Sans', sans-serif",
                }
            },
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
        }
        // , {
        //     name: name_2,
        //     data: timeseries['name_2']
        // }
        ]
    });
}