 
function initMap() {

var jsonString = '[{"name": ["Accepted", "Chapman University - One University Drive, Orange, California, USA", "Accepted", "Los Angeles, California, USA", "Accepted", "Veterans Hospital - 1611 Plummer Street, North Hills, Los Angeles, California, USA", "Accepted", "Walter Reed Middle School - 4525 Irvine Avenue, North Hollywood, Los Angeles, California, USA", "All I See Is You", "Bangkok, Thailand", "All I See Is You", "Barcelona, Spain", "All I See Is You", "Phuket, Thailand", "All I See Is You", "Thailand", "All I See Is You", "Spain"], "ycoord": [-117.85274505615234, -118.24368286132812, -118.47880554199219, -118.38660430908203, 100.50176239013672, 2.17340350151062, 98.33808898925781, 100.99253845214844, -3.74921989440918], "xcoord": [33.79330825805664, 34.0522346496582, 34.24287033081055, 34.15259552001953, 13.7563304901123, 41.38506317138672, 7.95193290710449, 15.87003231048584, 40.46366882324219]}]';

var myData = JSON.parse(jsonString);
var xcoordData = [];
var ycoordData = [];
var nameData = [];

$(document).ready(function() {
    $.each(myData, function() {
    	xcoordData = this.xcoord;
	ycoordData = this.ycoord;
        nameData = this.name;
    });
});

var xcoordStr = String(xcoordData);
var arrayXcoord = xcoordStr.split(',');
var ycoordStr = String(ycoordData);
var arrayYcoord = ycoordStr.split(',');


var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 1,
      center: new google.maps.LatLng(0, 0),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var infowindow = new google.maps.InfoWindow();

    var marker, i;
	

/* for (i = 0; i < arrayXcoord.length; i++) {  
    var latLng = new google.maps.LatLng(arrayXcoord[i], arrayYcoord[i]);
    
      marker = new google.maps.Marker({
        position: latLng,
        map: map	
      });

      google.maps.event.addListener(marker, 'click', (function(marker, i) {
        return function() {
          infowindow.setContent(nameData[i]);
          infowindow.open(map, marker);
        }
      })(marker, i));

}

}*/

 for (i = 0; i < arrayXcoord.length; i++) {  
      marker = new google.maps.Marker({
        position: new google.maps.LatLng(arrayXcoord[i], arrayYcoord[i]),
        map: map
      });

      google.maps.event.addListener(marker, 'click', (function(marker, i) {
        return function() {
          infowindow.setContent(nameData[i]);
          infowindow.open(map, marker);
        }
      })(marker, i));
    }
}
