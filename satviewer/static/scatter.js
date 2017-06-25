// Get the modal
var modal = document.getElementById('myModal');

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal
btn.onclick = function() {
  $('#map').hide();
    modal.style.display = "block";
    loadChart();


}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
      $('#map').hide();

}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
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
         title: 'NDVI vs LST scatterplot',
         hAxis: {title: 'LST', minValue: 20, maxValue: 25},
         vAxis: {title: 'NDVI', minValue: 0, maxValue: 0.5},

         legend: 'none',
         pointSize: 1,

       };

       var chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));

       chart.draw(dataTable, options);
     }

}
}