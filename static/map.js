var lastData = '';
function getMap(callback){
xmlhttp=new XMLHttpRequest();
xmlhttp.open("GET", "http://fa16-cs411-29.cs.illinois.edu:5000/markers", false);
xmlhttp.send();
//alert("AM I HERE");
callback(xmlhttp.responseText);
}


function initMap(){
var jsonString1 = '';

/*xmlhttp=new XMLHttpRequest();
xmlhttp.open("GET", "http://fa16-cs411-29.cs.illinois.edu:5000/static/markers.txt", false);
xmlhttp.send();
jsonString1 = xmlhttp.responseText;
*/

getMap(function(dataStuff){
console.log(dataStuff);
var start = "[";
var middle = dataStuff;
var end = "]";
var all = start.concat(middle);
var jsonString = all.concat(end);
//alert("hello");
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
//alert(arrayXcoord[0]);

var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 2,
      center: new google.maps.LatLng(0, 0),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var infowindow = new google.maps.InfoWindow();

    var marker, i;
	

 for (i = 0; i < arrayXcoord.length; i++) {  
      if(arrayXcoord[i]!='' && arrayYcoord[i]!=''){
	marker = new google.maps.Marker({
        position: new google.maps.LatLng(arrayXcoord[i], arrayYcoord[i]),
        map: map});
      
 
//      google.maps.event.addListener(marker, 'click', (function(marker, i) {
 //       return function() {
 //         infowindow.setContent(nameData[i]);
 //         infowindow.open(map, marker);
 //       }
 //     })(marker, i));
    }}
});

}


