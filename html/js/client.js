/*
 *      mio.js
 *
 *      Copyright 2012 indieCODE <ltw1129@web.cs.unibo.it>
 *
 *      This program is free software; you can redistribute it and/or modify
 *      it under the terms of the GNU General Public License as published by
 *      the Free Software Foundation; either version 2 of the License, or
 *      (at your option) any later version.
 *
 *      This program is distributed in the hope that it will be useful,
 *      but WITHOUT ANY WARRANTY; without even the implied warranty of
 *      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *      GNU General Public License for more details.
 *
 *      You should have received a copy of the GNU General Public License
 *      along with this program; if not, write to the Free Software
 *      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 *      MA 02110-1301, USA.
 *
 *
 */

var markers = {};
var map, geocoder, table, openinfo;
markers['you'] = map = geocoder = table = openinfo = null;
var directionsService = new google.maps.DirectionsService();
var directionsDisplay = new google.maps.DirectionsRenderer();

$('document').ready(function(){
    carica(0);
    caricamenu(1);
    $.ajaxSetup({
		timeout: 20000
	});
});

jQuery.fn.centra = function() {
    var altezza = $(window).height();
    var height = altezza * 0.9;
    this.css("height", height + $(window).scrollTop() + "px");
    return this;
}

jQuery.fn.leftmappa = function() {
	var width = ($('#maps').offset().left - $('#first').offset().left) * 0.95;
	var height = $('#first').height() - 10;
	this.css("width", width +"px");
	this.css("height", height+"px");
	return this;
}

jQuery.fn.rightmappa = function() {
	var width = ($('#first').offset().right - $('#drag1').offset().right) * 0.75;
    //var height = $('#maps').offset().top - $('#first').offset().bottom;
	this.css("width", width +"px");
	//this.css("height", height+"px");
	return this;
}

jQuery.fn.leftwidth = function() {
	var width = ($('#maps').offset().left - $('#first').offset().left) * 0.95;
	//var height = $('#first').height() - 10;
	this.css("width", width +"px");
	//this.css("height", height+"px");
	return this;
}
jQuery.fn.anima = function(a) {
	a? _animaleft(this) : _animaright(this);
	return this;
}

jQuery.fn.dataTableExt.oSort['num-html-asc']  = function(a,b) {
    var x = a.replace( /<.*?>/g, "" );
    var y = b.replace( /<.*?>/g, "" );
    x = parseFloat( x );
    y = parseFloat( y );
    return ((x < y) ? -1 : ((x > y) ?  1 : 0));
};

jQuery.fn.dataTableExt.oSort['num-html-desc'] = function(a,b) {
    var x = a.replace( /<.*?>/g, "" );
    var y = b.replace( /<.*?>/g, "" );
    x = parseFloat( x );
    y = parseFloat( y );
    return ((x < y) ?  1 : ((x > y) ? -1 : 0));
};

function anima(a) {
	var b = $('#first');
	a? _animaleft(b) : _animaright(b);
	return b;
}

function _animaleft(a) {
	a.css('position', 'relative');
	a.css('right', '0px');
	a.stop().animate({'right': '2000px'}, 1000, function() {
			a.css('right', '-2000px');
	});
}
function _animaright(a) {
	a.css('position', 'relative');
	a.css('right', '-2000px');
	a.stop().animate({'right': '0px'}, 1000, function() {
			//
	});
}

function avvisa(s) {
	$('#overlay').fadeIn('fast',function(){
			$('#overlay').click(function(){
				$('#box').animate({'top':'-200px'},500,function(){
					$('#overlay').fadeOut('fast');
				});
			});
			$('#box').html('<h1>Messaggio dal server:</h1><p>' + s + '</p>');
			$('#box').animate({'top':'160px'},500);
    });
}

function loading(bool) {
	if (bool) {
		avvisa('caricamento..');
	} else {
		$('#box').animate({'top':'-200px'},500,function(){
					$('#overlay').fadeOut('fast');
		});
	}
}

function rangefix(){
	//$("input[type='range']").rangeinput();
}

function creamappa(lat,long){
    $('#maps,#maps_container,#first').fadeIn();
    var myOptions = {
                center: new google.maps.LatLng(lat,long),
                zoom: 15,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
    map = new google.maps.Map(document.getElementById("maps"),myOptions);
    pulisci(markers);
    markers['you'] = new google.maps.Marker({
				position: new google.maps.LatLng(lat,long),
				draggable: true,
				animation: google.maps.Animation.DROP,
				map: map,
				title: 'tu sei qua!'
			});
}

function creatabella(data) {
	$('#drag1').html('<table cellpadding="0" cellspacing="0" border="0" class="display center" id="table"></table>').show();
	$('#table').dataTable({
            "aaData": data,
            "bJQueryUI": true,
            'bPaginate': false,
            "aaSorting": [[ 4,'desc']],
            "aoColumns": [
                {
                    "sTitle": "ID",
                    "fnRender": function(obj) {
                        var sReturn = obj.aData[ obj.iDataColumn ];
                        sReturn = "<a class='id_table' href=javascript:getinfotable('" + sReturn + "')>" + sReturn + "</p>";
                        return sReturn;
                    }
                },
                { "sTitle": "Nome" },
                {
                    "sTitle": "Categoria",
                    "fnRender": function(obj) {
                        var sReturn = obj.aData[obj.iDataColumn].toLowerCase();
                        if (( sReturn == "[u'supermarket']" ) || ( sReturn == "supermarket" )){
                            sReturn = "Supermercato";
                        }
                        else if ((sReturn == "[u'farmacia']") || (sReturn == "farmacia")){
                            sReturn = "Farmacia";
                        }
                        else if ((sReturn == "[u'scuola materna']") || (sReturn == "scuola materna")){
                            sReturn = "Scuola Materna";
                        }
                        else if ((sReturn == "[u'poste e telegrafi']") || (sReturn == "poste e telegrafi") || (sReturn == "[u'poste']")){
                            sReturn = "Posta";
                        }
                        else if ((sReturn == "[u'palestra']") || (sReturn == "palestra")){
                            sReturn = "Palestra";
                        }
                        else if (sReturn == "[u'banche']") {
                            sReturn = "Banca";
                        }
                        return sReturn;
                    }
                },
                { "sTitle": "Indirizzo", "sClass": "center" },
                {
                    "sTitle": "Distanza(linea d'aria)",
                    "asSorting": [ "num-html-asc", "num-html-desc" ],
                    "sClass": "center",
                    "fnRender": function(obj) {
                        var sReturn = parseFloat(obj.aData[ obj.iDataColumn ]);
                        if ( sReturn < 1000 ) {
                            sReturn = "<span class='distance1k'>"+ sReturn +"</span>";
                        }
                        else if (sReturn < 5000){
                            sReturn = "<span class='distance5k'>"+ sReturn +"</span>";
                        }
                        else {
                            sReturn = "<span class='distanceout'>"+ sReturn +"</span>";
                        }
                        return sReturn;
                    }
                }
            ]
        });
    $('#table_wrapper').leftmappa();
}

function carica(a){
    switch(a){
		case 0:
            $('#first').centra().load('static/menu.html', function() {
				anima(0);
				caricamenu(1);
			});
            break;
        case 1:
		$('#first').anima(1).load('static/vicinoa.html',function() {
			//rangefix();
			//$('#info').hide();
			$('#drag1').leftwidth();
			$('#first').anima(0);
			creamappa(44.5038496,11.335636);

            });
            break;
        case 2:
            //$('#first').anima(1).load('descrizione.html',function(){ $('#maps_container,#maps,#info').hide(); });
            //$('#first').anima(0);
            break;
        case 3:
		carica(1);
		caricamenu(1);
		break;
    }
}

function caricamenu(a){
	var def = "<ul class='menu'><li><a id='home' href='javascript:carica(0);'>home</a></li><li><a id='about' target='_blank' href='http://vitali.web.cs.unibo.it/TechWeb12/GruppoLTW021'>about</a></li>";
	switch(a) {
		case 1:
			$('#nav').html(def + '</ul>');
			break;
		case 2:
			$('#nav').html(def + "<li><a id='back' href='javascript:carica(3);'>back</a></li></ul>");
			break;
	}
	$('ul.menu a').stop().animate({'marginLeft':'-65px'},1000);
    $('ul.menu li').hover(
        function () {
            $('a',$(this)).stop().animate({'marginLeft':'-5px'},200);
        },
        function () {
            $('a',$(this)).stop().animate({'marginLeft':'-65px'},200);
        }
    );
}



function getinfotable(id) {
    var marker = markers[id];
    map.setCenter(markers[id].getPosition());
    google.maps.event.trigger(marker, 'click');
}

function marker(lat, long, id, map, aggr, category, data) {
    var icon;
    category = category.toLowerCase();
    if ((category == "[u'supermarket']") || (category == "supermarket")) {
        icon = 'images/mural.png';
    }
    else if ((category == "[u'farmacia']") || (category == "farmacia")) {
        icon = 'images/medicine.png';
    }
    else if ((category == "[u'poste e telegrafi']") || (category == "poste e telegrafi") || (category == "[u'poste']")) {
        icon = 'images/aboriginal.png';
    }
    else if ((category == "[u'scuola materna']") || (category == "scuola materna")) {
        icon = 'images/walkingtour.png';
    }
    else if ((category == "[u'palestra']") || (category == "palestra")) {
        icon = 'images/ropescourse.png';
    }
    else if (category == "[u'banche']") {
        icon = 'images/waterwell.png';
    }
    else {
        icon = 'images/fireworks.png';
    }
    var latlng = new google.maps.LatLng(lat,long);
    var mark = new google.maps.Marker({
        position: latlng,
        icon: icon,
        map: map,
        animation: google.maps.Animation.DROP,
        title: id
    });
    google.maps.event.addListener(mark, 'click', function() {
		descrizione(data,mark,aggr,id);
		percorso(markers['you'].getPosition(),latlng);
    });
    return mark;
}

function percorso(p1,p2) {
	directionsDisplay.setMap(null);
	var request = {
        origin:p1,
        destination:p2,
        travelMode: google.maps.DirectionsTravelMode.WALKING
    };
    directionsService.route(request, function(response, status) {
      if (status == google.maps.DirectionsStatus.OK) {
        directionsDisplay.setDirections(response);
      }
    });
    directionsDisplay.setMap(map);
}

function descrizione(data,mark,aggr,id) {
	var position = mark.getPosition();
	if (openinfo != null) openinfo.close();
	var date = new Date();
	var giorni = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
	var ore = ["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23"];
	var minuti = ["00","01","02","03","04","05","06","07","08","09"];
	for (i=10;i<60;i++) minuti[i] = i;
	var data2 = giorni[date.getDay()] + ': ' + ore[date.getHours()] + minuti[date.getMinutes()] + '-' + ore[date.getHours() + 1] + '30.';
	var url = 'http://ltw1135.web.cs.unibo.it/aprira/params/' + data + '/' + data2;
	var url2 = 'http://ltw1129.web.cs.unibo.it/descrizione/' + aggr + '/params/' + id;
	$.ajax({ //descrittore 'aprirà' acquistato da eggs and beacon
		type: 'GET',
		url: url,
		dataType: 'html',
		accept: 'text/html',
		success: function(res){
				switch(res){
					case "0": res = '<p style="color:red;">chiuso'; break;
					case "1": res = '<p style="color:orange;">aperto, ma chiuderà'; break;
					case "2": res = '<p style="color:yellow;">chiuso, ma aprirà'; break;
					case "4": res = '<p style="color:green;">aperto</p>'; break;
					default: res = '';
				}
				$.ajax({ //descrittore 'descrizione'
					type: 'GET',
					url: url2,
					dataType: 'html',
					accept: 'text/html',
					success: function(content){
						openinfo = new google.maps.InfoWindow();
						openinfo.setContent(content + ' ' + res + '<p><a href=javascript:cosafaccio(' + position.lat() + ',' + position.lng() + ')> cerca altri posti vicino </a></p>');
						openinfo.open(map,mark);
					}
				});

		}
	});
}

function cosafaccio(lat,long) { //descrittore 'cosa faccio oggi' acquistato da creeping penguins
	var RT = 6372795.477598
	var radlatA = lat * (Math.PI / 180.0)
	var radlonA = long * (Math.PI / 180.0)
    	loading(true);
    	anima(1);
    	//creamappa(lat,long); //non ricreare la mappa ogni volta
	var giorni = ["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31"]
	var date = new Date();
	var datastr = date.getFullYear() + '-' + giorni[date.getMonth() + 1] + '-' + giorni[date.getDate()];
   	var url = 'http://ltw1130.web.cs.unibo.it/thcfo/ltw1129-super/ltw1129-farmacie/ltw1129-poste/ltw1129-scuole/ltw1129-scuolern/ltw1129-postern/ltw1129-farmaciern/ltw1129-superrn/params/' + lat + '/' + long + '/' + datastr + '/banche/farmacia/supermarket/scuola materna/palestra/poste/mod-vicinanza';
	$.getJSON(url, function(){

    	})
   	.success(function(data, status, jqhxr){
        var aadata = new Array();
        var res = 0;
        var partenza = new google.maps.Marker({position:new google.maps.LatLng(lat,long), map: map});
        $.each(data.locations,function(key, val){
            markers[key] = marker(val['lat'],val['long'],key,map,'ltw1129-super/ltw1129-farmacie/ltw1129-poste/ltw1129-scuole/ltw1129-scuolern/ltw1129-postern/ltw1129-farmaciern/ltw1129-superrn/ltw1129-palestrern',val['category'],val['opening']);
            var radlatB = val['lat'] * (Math.PI / 180.0)
			var radlonB = val['long'] * (Math.PI / 180.0)
            var distance = RT * Math.acos(Math.sin(radlatA) * Math.sin(radlatB) + Math.cos(radlatA) * Math.cos(radlatB) * Math.cos(radlonA - radlonB));
            aadata[res++] = new Array(key,val['name'],val['category'],val['address'],distance);
        });
        creatabella(aadata);
        loading(false);
        caricamenu(2);
        anima(0);
	})
	.error(function(jqHXR, status) {
		avvisa(status +': ' + jqHXR.status +'</p><p>i server probabilmente sono giù, clicca <a href="http://www.downforeveryoneorjustme.com/' + url + '">qui</a> per controllare.');
		carica(1);
	})
}

function vicinoa(lat,long,aggr,max,distance){
	pulisci(markers);
	//creamappa(lat,long); // non ricreare la mappa ogni volta

	var url = '';
	if (max == '' || distance == '') {
	url = 'http://ltw1129.web.cs.unibo.it/vicinoa/' + aggr + '/params/' + lat + '/'+ long;
	}
	else if (max == '') {
	url = 'http://ltw1129.web.cs.unibo.it/vicinoa/' + aggr + '/params/' + lat + '/'+ long + '/50/' + distance;
	}
	else if (distance == '') {
	url = 'http://ltw1129.web.cs.unibo.it/vicinoa/' + aggr + '/params/' + lat + '/'+ long + '/' + max;
	}
	else {
	url = 'http://ltw1129.web.cs.unibo.it/vicinoa/' + aggr + '/params/' + lat + '/'+ long + '/' + max + '/' + distance;
	}

	$.getJSON(url, function(){
	/**/
	})
	.success(function(data, status, jqhxr){
	var aadata = new Array();
	var res = 0;
	$.each(data.locations,function(key, val){
	    markers[key] = marker(val['lat'],val['long'],key,map,aggr,val['category'],val['opening']);
	    aadata[res++] = new Array(key,val['name'],val['category'],val['address'],parseFloat(val['distance']));
	});
	creatabella(aadata);
	$('#maps,#maps_container').css('padding-top', $('#first').height() * 0.05);
	loading(false);
	caricamenu(2);
	anima(0);
	})
	.error(function(jqHXR, status) {
		avvisa(status +': ' + jqHXR.status +'</p><p>i server probabilmente sono giù, clicca <a href="http://www.downforeveryoneorjustme.com/' + url + '">qui</a> per controllare.');
		carica(1);
	})
	try {
		aadata = null;
	} catch (e){/**/}
};

function pulisci(hash){
	$.each(hash,function(key){
		if (key != 'you') {
			hash[key].setMap(null);
			delete hash[key];
		}
    	})
}
function initialize(geo) {
    var lat,long;
    loading(true);
    anima(1);
    $('#footer,.titoletto,#drag1,#more').hide();
    $('#maps,#first').fadeIn();
	switch (geo) {
			case 0:
				if(navigator.geolocation) {
					var t;
					if (markers['you'] != null)	markers['you'].setMap(null);
					navigator.geolocation.getCurrentPosition(function(position) {
							pos = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
							lat = position.coords.latitude;
							long = position.coords.longitude;
							clearTimeout(t);
							map.setCenter(pos);
							markers['you'] = new google.maps.Marker({
								position: pos,
								draggable: true,
								animation: google.maps.Animation.DROP,
								map: map,
								title: 'tu sei qua!'
							});
							openinfo = new google.maps.InfoWindow({
								content: 'tu sei qua!'
							});
							openinfo.open(map,markers['you']);
							var distance = document.getElementById('distance').value;
							var aggr = document.getElementById('select').value;
							var max = document.getElementById('max').value;
							vicinoa(lat,long,aggr,max,distance);
					}, function(error) {
							avvisa('Error: The Geolocation service failed. (' + error + ')');
							loading(false);
							},
							{
							enableHighAccuracy: true,
							timeout: 7500
							});
						t = setTimeout(function () {
							carica(1);
							loading(false);
						}, 7500);

				} else {
					avvisa("Error: Your browser doesn't support geolocation.");
					loading(false);
				}
				break;
			case 1:
				lat = markers['you'].getPosition().lat();
				long = markers['you'].getPosition().lng();
				var distance = document.getElementById('distance').value;
				var aggr = document.getElementById('select').value;
				var max = document.getElementById('max').value;
				vicinoa(lat,long,aggr,max,distance);
				break;
			case 2:
				if (document.getElementById('address').value == '') {
					carica(1);
					avvisa('devi inserire un indirizzo per continuare..');
					break;
				}
				markers['you'].setMap(null);
				geocoder = new google.maps.Geocoder();
				geocoder.geocode( {'address': document.getElementById('address').value }, function(results,status) {
					if (status == google.maps.GeocoderStatus.OK) {
						var location = results[0].geometry.location;
						map.setCenter(location);
						markers['you'] = new google.maps.Marker({position: location, map: map});
						lat = markers['you'].getPosition().lat();
						long = markers['you'].getPosition().lng();
						var distance = document.getElementById('distance').value;
						var aggr = document.getElementById('select').value;
						var max = document.getElementById('max').value;
						vicinoa(lat,long,aggr,max,distance);
					} else {
						avvisa("Problema nella ricerca dell'indirizzo: " + status);
					}
				});
				break;
	}
}

