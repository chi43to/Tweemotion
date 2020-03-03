var dictionnary = '{{ geocode_js|tojson }};'
var mymap = L.map('mapid');
var feelings = '{{feelings_js|tojson}}';
var new_feelings = JSON.parse(feelings);

  document.getElementById("neshto").innerHTML = JSON.stringify(new_feelings);

function getmax(reg) {
  flg = "";
  max = 0;
  for(var each in new_feelings[reg]) {
    if(new_feelings[reg].hasOwnProperty(each)) {    
      if(new_feelings[reg][each]>max) {
        max = new_feelings[reg][each];
       flg = each;
    }

}
}

result = [];
result.push(flg,max);
return result;
}


 L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	 tilesize: 512,
  zoomOffset: -1,
    id: 'mapbox/dark-v10',
    accessToken: 'pk.eyJ1IjoibmlraWJnOTMiLCJhIjoiY2s2NDlpZnIxMGVwdTNvcGJ3dnI4Mmh3NiJ9.OCzqmlwMExgA6uDj8biVVw'
}).addTo(mymap);

 of = JSON.parse(truc.slice(0,-1));
 var arr = [];
 for(var each in of) {
  var value = of[each];
  arr.push(value);
 }
var vounds = new L.LatLngBounds(arr);
var i = 0;
for(var cd in arr) {
  var opa = getmax(Object.keys(new_feelings)[i]);
  if(opa[0]!="") {
  var circle = L.circle(arr[cd], {
      "fillcolor":"#f03",
      "color":"red",
      "fillOpacity":0.5,
      "radius": 7000,
  }).bindTooltip(opa[0],{permanent: false}).addTo(mymap);
}
  i=i+1;
}

mymap.fitBounds(vounds);

