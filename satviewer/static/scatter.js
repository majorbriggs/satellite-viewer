var chart = null;
var dataTable = null;

function loadChart(){
    if (dataJson != ""){
        google.charts.load('current', {'packages':['corechart']});
        google.charts.setOnLoadCallback(drawChart);
        chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));
    }
}

function drawChart() {
    dataTable = new google.visualization.DataTable();
    dataTable.addColumn("number", "TS");
    dataTable.addColumn("number", "NDVI");
    dataTable.addColumn("number", "longitude");
    dataTable.addColumn("number", "latitude");

    dataTable.addRows(dataJson["points"]);
    var pixelsDetails = "";
    if (dataJson["downsampled"]) {
        pixelsDetails += "Number of points: " + dataJson["downsampled_size"] + " (downsampled from " + dataJson["original_size"] + ")";
    }
    else {
        pixelsDetails += "Number of points: " + dataJson["original_size"];
    }
    var options = {
     title: 'Ts / VI scatterplot.\n' + pixelsDetails,
     vAxis: {title: 'VI',
     viewWindowMode:'explicit',
     viewWindow: {
              max:-0.5,
              min:1.0
            }},
     hAxis: {title: 'Ts [\u2103]', viewWindowMode:'explicit',
            viewWindow: {
              max:15,
              min:40
            }},
     pointSize: 1,
     legend: 'none',

     height: 390,
    };


    // Listen for the 'select' event, and call my function selectHandler() when
    // the user selects something on the chart.
    google.visualization.events.addListener(chart, 'select', selectHandler);
    var view = new google.visualization.DataView(dataTable);
    view.setColumns([0,1]);
    chart.draw(view, options);
}

function selectHandler() {
    var selectedItem = chart.getSelection()[0];
    if (selectedItem) {
        var lat = dataTable.getValue(selectedItem.row, 3);
        var lng = dataTable.getValue(selectedItem.row, 2);
        var newLatLng = new L.LatLng(lat, lng);
        marker.setLatLng(newLatLng);
        marker.addTo(map);
    }
}