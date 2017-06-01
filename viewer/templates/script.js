
window.onload=function(){
    var map = L.map('map', {
          zoomControl: false
    }).setView([54.366667, 18.633333], 9);
    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 17,
    id: 'mapbox.satellite',
    accessToken: 'pk.eyJ1IjoibWFqb3JicmlnZ3MiLCJhIjoiY2l2dHozbXdrMDA0dzJ6bHVqMWV3aHhoYyJ9.LksFMcYK2pG_TAEtn7J9Gg'
    }).addTo(map);
	dateRangeAjax();
    percentageSlider("#clouds-range", "#clouds-amount", 0, 50);
    percentageSlider("#data-range", "#data-amount", 0, 50);

}


function percentageSlider(slider_id, amount_id, start_min, start_max)
{
    $( slider_id ).slider
    (
      {
        range: true,
        min: 0,
        max: 100,
        values: [ start_min, start_max ],
        slide: function( event, ui )
          {
            $( amount_id ).val( ui.values[ 0 ] + "% - " + ui.values[ 1 ] + "%");
          },
        change: function( event, ui ){
            filterWithAjax();
        }

      }

    )
    $( amount_id ).val( $( slider_id ).slider( "values", 0 ) + "% - " + $( slider_id ).slider( "values", 1 ) + "%");
};

function dateRangeAjax()
{
	$.ajax
      (
        {
          type: 'GET',
          url: 'http://localhost:8000/api/images/dates',
          dataType: 'json',
          success: function(response)
            {

              if (response)
                {
                  date_min = Date.parse(response.date__min)/1000;
                  date_max = Date.parse(response.date__max)/1000;
    			  dateSlider("#date-range", "#date-amount", date_min, date_max);
                }
            }
        }
      );
}



function filterWithAjax()
{
    $.ajax
      (
        {
          type: 'GET',
          url: 'http://localhost:8000/api/images/',
          dataType: 'json',
          data:
            {
              clouds_min: $( "#clouds-range" ).slider( "values", 0 ),
              clouds_max: $( "#clouds-range" ).slider( "values", 1 ),
              data_min: $( "#data-range" ).slider( "values", 0),
              data_max: $( "#data-range" ).slider( "values", 1),
              date_min: formatDT(new Date($( "#date-range" ).slider( "values", 0)*1000)),
              date_max: formatDT(new Date($( "#date-range" ).slider( "values", 1)*1000)),
            },
          success: function(response)
            {

              if (response)
                {
                  txt = buildImagesList(response);
                  console.log(txt);
                  if (txt != "")
                  {
                    $("#images-list").html(txt);
                  }
                }
            }
        }
      );
}

function formatDT(__dt) {
    var year = __dt.getFullYear();
    var month = zeroPad(__dt.getMonth()+1, 2);
    var date = zeroPad(__dt.getDate(), 2);
    var hours = zeroPad(__dt.getHours(), 2);
    var minutes = zeroPad(__dt.getMinutes(), 2);
    var seconds = zeroPad(__dt.getSeconds(), 2);
    return year + '-' + month + '-' + date;
};

function zeroPad(num, places) {
  var zero = places - num.toString().length + 1;
  return Array(+(zero > 0 && zero)).join("0") + num;
}



function dateSlider(slider_id, amount_id, date_min, date_max)
{
    $( slider_id ).slider
    (
      {
        range: true,
        min: date_min,
        max: date_max,
        values: [ date_min, date_max ],
        slide: function( event, ui )
          {
            $( amount_id ).val( formatDT(new Date(ui.values[ 0 ] * 1000)) + " to " + formatDT(new Date(ui.values[ 1 ] * 1000)));
          },
        change: function( event, ui ){
            filterWithAjax()
        }
      }
    )
    $( amount_id ).val( formatDT(new Date($( slider_id ).slider( "values", 0 ) * 1000)) + " to " + formatDT(new Date($( slider_id ).slider( "values", 1 ) * 1000)));
};

function buildImagesList(response){
  var len = response.length;
  var start = '<ul>';
  var txt = '';
  for (var i=0; i<len; i++){
    imgObject = response[i];
    txt += '<li><div class="image-entry"><table><tr><td><span class="label">Image ID: </span></td><td><span class="value">'+imgObject.aws_bucket_uri+'</span></td></tr>';
    txt += '<tr><td><span class="label">Data:</span></td><td><span class="value">'+imgObject.data_percentage+'%</span></td></tr>';
    txt += '<tr><td><span class="label">Clouds:</span></td><td><span class="value">'+imgObject.clouds_percentage+'%</span></td></tr>';
    txt += '<tr><td><span class="label">Date:</span></td><td><span class="value">'+imgObject.date+'</span></td></tr></table></div></li>';
  }
  var end = "</ul>";
  return start + txt + end;
}

