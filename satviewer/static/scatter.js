// Get the modal
var modal = document.getElementById('myModal');
var modalInfo = document.getElementById('infoModal');
var btnInfo = document.getElementById("btn-ts-vi-info");


btnInfo.onclick = function (){
    modalInfo.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
$(document).on('click', '.close', function() {
    modal.style.display = "none";
    modalInfo.style.display = "none";
}
);
// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal || event.target == modalInfo) {
        event.target.style.display = "none";
    }
}

function loadChart(){

if (dataJson != ""){

google.charts.load('current', {'packages':['corechart']});
     google.charts.setOnLoadCallback(drawChart);
     function drawChart() {
       var dataTable = new google.visualization.DataTable();
       dataTable.addColumn("number", "NDVI");
       dataTable.addColumn("number", "TS");
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
         vAxis: {title: 'Ts', minValue: 20, maxValue: 25},
         hAxis: {title: 'VI', minValue: 0, maxValue: 0.5},
         legend: 'none',
         pointSize: 1,
         height: 390,
       };

       var chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));
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

        // Listen for the 'select' event, and call my function selectHandler() when
        // the user selects something on the chart.
        google.visualization.events.addListener(chart, 'select', selectHandler);
        var view = new google.visualization.DataView(dataTable);
        view.setColumns([0,1]);
       chart.draw(view, options);
     }

}
}