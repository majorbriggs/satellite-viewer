window.onload=function(){
    setupMap();

	  dateRangeAjax();
    percentageSlider("#clouds-range", "#clouds-amount", 0, 50);
    percentageSlider("#data-range", "#data-amount", 0, 100);

    $(document).on('click', '.image-entry', function() {requestImage(this);});
}


var temperatureStyle = 'temperature';
var ndviStyle = 'ndvi';
var dataJson = "";
var WORKSPACE = 'sat-viewer'
var RGB = 'RGB';
var NDVI = 'NDVI';
var TEMP = 'TEMP';
var stateOfLayers = new Array(true, false, false); 
var currentSceneID = "";
var selected_image_element = null;
var tsLayer = getWMSLayer(currentSceneID, TEMP, temperatureStyle);
var ndviLayer = getWMSLayer(currentSceneID, NDVI, ndviStyle);
var rgbLayer = getWMSLayer(currentSceneID, RGB, '');
var tsviSelection = null;

var earthLayer = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 17,
        id: 'mapbox.satellite',
        accessToken: 'pk.eyJ1IjoibWFqb3JicmlnZ3MiLCJhIjoiY2l2dHozbXdrMDA0dzJ6bHVqMWV3aHhoYyJ9.LksFMcYK2pG_TAEtn7J9Gg'
        });

var baseMaps = {
    "Earth": earthLayer,

};

var overlayMaps = {
    "RGB": rgbLayer,
    "NDVI": ndviLayer,
    "TS": tsLayer,
};
var map = L.map('map', {
    center: [54.366667, 18.633333],
    zoom: 10,
    zoomControl:false,
    layers: [earthLayer]
});


map.on('overlayadd', onOverlayAdd);
map.on('overlayremove', onOverlayRemove);


function onOverlayAdd(e){
  if (e.name === RGB){
    stateOfLayers[0] = true;
  } else if (e.name === NDVI){
    stateOfLayers[1] = true;
  } else if (e.name === 'TS'){
    stateOfLayers[2] = true;
  } 
}

function onOverlayRemove(e){
  if (e.name === RGB){
    stateOfLayers[0] = false;
  } else if (e.name === NDVI){
    stateOfLayers[1] = false;
  } else if (e.name === 'TS'){
    stateOfLayers[2] = false;
  } 
}

function restoreLayersSelection(){
  for (var i = 0; i<stateOfLayers.length; i++){
    if (stateOfLayers[i]){
      var layerControlElement = document.getElementsByClassName('leaflet-control-layers')[0];
      layerControlElement.getElementsByTagName('input')[i+1].click();
    }
  }
  
}
var control = null;


function getLayerName(sceneID, type){
    return WORKSPACE + ":" + sceneID.split('__')[1] + "_" + type;

}
function updateLayers(){
    sTemp = stateOfLayers.slice();
    tsLayer.removeFrom(map);
    ndviLayer.removeFrom(map);
    rgbLayer.removeFrom(map);
    stateOfLayers = sTemp;
    tsLayer = getWMSLayer(currentSceneID, TEMP, temperatureStyle);
    ndviLayer = getWMSLayer(currentSceneID, NDVI, ndviStyle);
    rgbLayer = getWMSLayer(currentSceneID, RGB, '');

    var baseMaps = {
        "Earth": earthLayer,

    };

    var overlayMaps = {
        "RGB": rgbLayer,
        "NDVI": ndviLayer,
        "TS": tsLayer,
    };

    if (control !== null){
      control.remove();
    }
    control = L.control.layers(baseMaps, overlayMaps, {collapsed:false});
    control.setPosition('verticalcenterright');
    control.addTo(map);

    restoreLayersSelection();
    if (tsviSelection != null){
      windowAjax(tsviSelection);
    }

}

function setupMap()
{


    addControlPlaceholders(map);


    updateLayers();

    drawnItems = L.featureGroup();
    map.addLayer(drawnItems);

    var myStyle = {
        "color": "#000000",
        "weight": 2,
        "opacity": 0.65,
        "dashArray": '5, 5',
    };  
    var drawControlAdd = new L.Control.Draw({
        draw: {
            polygon: false,
            circle: false,
            polyline: false,
            marker: false,
            rectangle: {shapeOptions: myStyle},
        },
        position: 'bottomright'
    });



    var drawControlEditOnly = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: false,
        position: 'bottomright',
    });

    map.addControl(drawControlAdd);

    map.on(L.Draw.Event.CREATED, function (e) {
        tsviSelection = e.layer;
        tsviSelection.addTo(drawnItems);
        drawControlAdd.remove();
        drawControlEditOnly.addTo(map)
        windowAjax(tsviSelection);
    });

    map.on(L.Draw.Event.EDITED, function (e) {
      tsviSelection = e.layers._layers[Object.keys(e.layers._layers)[0]];
      windowAjax(tsviSelection);
    });

    map.on(L.Draw.Event.DELETED, function(e) {
        check =  Object.keys(drawnItems._layers).length;

        if (check === 0){
            drawControlEditOnly.remove();
            drawControlAdd.addTo(map);
        };
        tsviSelection = null;

    });
    map._onResize();
}

function windowAjax(layer)
{
  var NE_lat = layer._bounds._northEast.lat;
  var NE_lng = layer._bounds._northEast.lng;
  var SW_lat = layer._bounds._southWest.lat;
  var SW_lng = layer._bounds._southWest.lng;
  $.ajax
      (
        {
          type: 'GET',
          url: 'api/tsvi',
          dataType: "json",
          data:
            {
              imageId: currentSceneID,
              neLat: NE_lat,
              neLng: NE_lng,
              swLat: SW_lat,
              swLng: SW_lng
            },
          success: function(response)
            {
              dataJson = response;
            }
        }
      );
}

function addControlPlaceholders(map) {
    var corners = map._controlCorners,
        l = 'leaflet-',
        container = map._controlContainer;

    function createCorner(vSide, hSide) {
        var className = l + vSide + ' ' + l + hSide;

        corners[vSide + hSide] = L.DomUtil.create('div', className, container);
    }

    createCorner('verticalcenter', 'left');
    createCorner('verticalcenter', 'right');
}

function getWMSLayer(sceneID, type, style){
    return L.tileLayer.wms(geoServerUrl + "sat-viewer/wms", {
    layers: getLayerName(sceneID, type),
    styles: style,
    format: 'image/png',
    transparent: true,
});
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
          url: '/api/images/dates',
          dataType: 'json',
          success: function(response)
            {

              if (response)
                {
                  date_min = Date.parse(response.date__min)/1000;
                  date_max = Date.parse(response.date__max)/1000;
    			  dateSlider("#date-range", "#date-amount", date_min, date_max);
    			  filterWithAjax();
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
          url: '/api/images/',
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
    txt += '<li><div class="image-entry"><table>';
    txt += '<tr><td><span class="label">Source: </span></td><td class="value"><span class="value">'+imgObject.source+'</span></td></tr>';
    txt += '<tr><td><span class="label">Image ID: </span></td><td class="image-id"><span class="value">'+imgObject.aws_bucket_uri+'</span></td></tr>';
    txt += '<tr><td><span class="label">Data:</span></td><td><span class="value">'+imgObject.data_percentage+'%</span></td></tr>';
    txt += '<tr><td><span class="label">Clouds:</span></td><td><span class="value">'+imgObject.clouds_percentage+'%</span></td></tr>';
    txt += '<tr><td><span class="label">Date:</span></td><td><span class="value">'+imgObject.date+'</span></td></tr></table></div></li>';
  }
  var end = "</ul>";
  return start + txt + end;
}


function requestImage(element){
  currentSceneID = $(element).find($('.image-id')).text();
  if (selected_image_element !== null){
    $(selected_image_element).removeClass('image-selected');
  }
  selected_image_element = element;
  $(selected_image_element).addClass('image-selected');
  updateLayers();
	// image_uri = $(element).find($('.image-id')).text();
 //  $.ajax
 //      (
 //        {
 //          type: 'GET',
 //          url: '/api/image',
 //          dataType: 'json',
 //          data:
 //            {
 //              image_uri: image_uri,
 //            },
 //          success: function(response)
 //            {
 //              if (response)
 //                {
 //                  alert("Queue msg id: " + response.message_id);

 //                }
 //            }
 //        }
 //      );
}

