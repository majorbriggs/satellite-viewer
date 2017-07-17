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
    $('#map').hide();
    modal.style.display = "block";
    loadChart();
}

}


function showError(){
    modalError.style.display = "block";
    $('#map').hide();
}


btnInfo.onclick = function (){
  $('#map').hide();
    modalInfo.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
$(document).on('click', '.close', function() {
    modal.style.display = "none";
    modalInfo.style.display = "none";
      $('#map').show();

}
);
// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal || event.target == modalInfo || event.target == modalError) {
        event.target.style.display = "none";
        $('#map').show();

    }
}

function loadChart(){

if (dataJson != ""){

google.charts.load('current', {'packages':['corechart']});
     google.charts.setOnLoadCallback(drawChart);
     function drawChart() {
       var dataTable = new google.visualization.arrayToDataTable(dataJson)

       var options = {
         title: 'Ts / VI scatterplot',
         vAxis: {title: 'Ts', minValue: 20, maxValue: 25},
         hAxis: {title: 'VI', minValue: 0, maxValue: 0.5},
         legend: 'none',
         pointSize: 1,
         height: 400,

       };

       var chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));

       chart.draw(dataTable, options);
     }

}
}