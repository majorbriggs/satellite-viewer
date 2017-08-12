// Get the modal
var modal = document.getElementById('myModal');
var modalInfo = document.getElementById('infoModal');
var modalError = document.getElementById('errorModal');

// Get the button that opens the modal
var btn = document.getElementById("btn-show-ts-vi");


var btnInfo = document.getElementById("btn-ts-vi-info");

// Get the <span> element that closes the modal

// When the user clicks on the button, open the modal
btn.onclick = function() {
  if (tsviSelection == null){
      showError("Select area for TSVI scatterplot");
  }
  else{
    // modal.style.display = "block";
    loadChart();
    $('#area-snapshot').attr('src', areaSnapshotUrl);
}

}


function showError(){
    modalError.style.display = "block";
}


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
    if (event.target == modal || event.target == modalInfo || event.target == modalError) {
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
       dataTable.addRows(dataJson["points"]);
       var pixelsDetails = "";
       if (dataJson["downsampled"]) {
            pixelsDetails += "Number of points: " + dataJson["downsampled_size"] + " (downsampled from " + dataJson["original_size"] + ")";
       }
       var options = {
         title: 'Ts / VI scatterplot.\n' + pixelsDetails,
         vAxis: {title: 'Ts', minValue: 20, maxValue: 25},
         hAxis: {title: 'VI', minValue: 0, maxValue: 0.5},
         legend: 'none',
         pointSize: 1,
         height: 390

       };

       var chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));

       chart.draw(dataTable, options);
     }

}
}