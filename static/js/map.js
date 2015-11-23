
var map;
var places;
var geocoder;
var autocomplete;
var userCoords;
var userMarker;

// Map filter defaults (displays all markers)
var onlyShow = {"acceptAnimals": false,
                "acceptVolunteers": false,
                "animals": [],
                };

function initMap() {
  var animalTypes = {};

  // HTML5 geolocation
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };

      userCoords = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
      console.log(position.coords);
      map.setCenter(pos);
      dropUserMarker(userCoords);
    });
  } else {
    var otherpos = {lat: 47.29247, lng: -120.39987};
    map.setCenter(otherpos);
  }

  // Create map and set zoom
  map = new google.maps.Map(document.getElementById('main-map'), {
    zoom: 9
  });

  // Create user marker
  createUserMarker();

  // Geocoder
  geocoder = new google.maps.Geocoder();

  // Address Autocomplete
  var loc = document.getElementById('address-entry');
  var locOptions = {};

  autocomplete = new google.maps.places.Autocomplete(loc, locOptions);
  places = new google.maps.places.PlacesService(map);

  autocomplete.addListener('place_changed', addressAutocompleted);

// Create info window
var infoWindow = new google.maps.InfoWindow({
      width: 500
  });

var markerArray = [];

$.get('/animals.json', function (animals) {
    for (var key in animals) {
      animal = animals[key];
      animalTypes[key] = animal.typeName;
    }
});

console.log(animalTypes);

  // Grab marker JSON with AJAX
  $.get('/orgs.json', function (orgs) {

      var org, marker, html, printAddress, orgPhoto, windowClass, orgAnimals;


      for (var key in orgs) {
          org = orgs[key];
          orgPhoto = '<span></span>';
          windowClass = 'single-col-window';
          orgAnimals = ' ';

          var markerIcon = 'generic';
          if (org.animals.length < 5 & org.animals.length > 0) {
            var randomIndex = Math.floor(Math.random() * org.animals.length);
            markerIcon = org.animals[randomIndex];
          }

          var acceptVolunteers = org.accept_volunteers;

          // Define the marker
          marker = new google.maps.Marker({
              position: new google.maps.LatLng(org.latitude, org.longitude),
              map: map,
              animation: google.maps.Animation.DROP,
              title: org.orgName,
              icon: 'static/img/wildally_marker_' + markerIcon + '.png#' + key,
          });

          // Adding some special attributes to each marker object
          marker.orgId = key;
          marker.intake = org.acceptAnimals;
          marker.volunteers = org.acceptVolunteers;
          marker.animals = org.animals;

          // Add the new marker to the markerArray
          markerArray.push(marker);

          if (org.photoFilenames !== null) {
              windowClass = 'double-col-window';
              orgPhoto = '<div class="window-left"><img class="infowindow-photo" src=' +
              org.photoRoot + '/' + org.photoFilenames[0] + '></div>';
          }

          if (org.photoFilenames !== null){
          if (org.photoFilenames.length == 1) {
              windowClass = 'double-col-window';
              orgPhoto = '<div class="window-left"><img class="infowindow-photo" src=' + org.photoRoot + '/' + org.photoFilenames[0] + '></div>';
          } else {
              windowClass = 'double-col-window';
              var carousel = '<div class="window-left"><div id="myCarousel" class="carousel slide" data-ride="carousel" data-interval="2000">';
              var indicators = '<ol class="carousel-indicators">' +
                                '<li data-target="#myCarousel" data-slide-to="0" class="active"></li>';
              var slides = '<div class="carousel-inner" role="listbox">' +
                           '<div class="item active">' +
                           '<img src=' + org.photoRoot + '/' + org.photoFilenames[0] + '>' +
                           '</div>';
              var controls = '<a class="left carousel-control" href="#myCarousel" role="button" data-slide="prev">' +
                             '<span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>' +
                             '<span class="sr-only">Previous</span></a>' +
                             '<a class="right carousel-control" href="#myCarousel" role="button" data-slide="next">' +
                             '<span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>' +
                             '<span class="sr-only">Next</span></a>';
              for (i = 1; i < org.photoCount; i++) {
                  indicators = indicators.concat('<li data-target="#myCarousel" data-slide-to="' + i + '"></li>');
              }
              indicators = indicators.concat('</ol>');
              for (i = 1; i < org.photoFilenames.length; i++){
                  slides = slides.concat('<div class="item"><img src=' +  org.photoRoot + '/' + org.photoFilenames[i] + '></div>');
              }
              slides = slides.concat('</div>');
              carousel = carousel.concat(indicators);
              carousel = carousel.concat(slides);
              carousel = carousel.concat(controls);
              carousel = carousel.concat('</div></div>');

              orgPhoto = carousel;
          }
        }

          if (org.address1) {
              if (org.address2 && org.show_address == 1) {
                  printAddress = org.address1 + '<br />' + org.address2;
              } else if (org.show_address == 1) {
                  printAddress = org.address1 + '<br />'; }
          } else { printAddress = 'This is an approximate location. Please call for directions. <br /><br />'; }

          if (org.animals.length == 5) {
              orgAnimals = '<li>all wildlife</li>';
          } else {
              for (i = 0; i < org.animals.length; i++) {
                  orgAnimals = orgAnimals.concat('<li>' + animalTypes[org.animals[i]] + '</li>');
              }
            }

          // Define the content of the infoWindow
          html = (
              '<div class="window-content ' + windowClass + '">' +
                  orgPhoto +
              '<div class="window-right">' +
                  '<h3>' + org.orgName + '</h3>' +
                  '<a href="tel:' + org.phone + '">' + 
                  '<h4 class="' + org.phone + '"><span class="glyphicon glyphicon-earphone" aria-hidden="true"></span> &nbsp;' +
                  org.phone + '</h4></a>' +
                  '<p>' + printAddress +
                        org.city + ', ' +
                        org.state + ' ' +
                        org.zipcode +
                  '</p>' + '<p>' + org.desc + '</p>' +
                  '<h5>Animals accepted</h5><ul>' + orgAnimals + '</ul>' +
              '</div>' +
              '</div>');

          // Inside the loop we call bindInfoWindow passing it the marker,
          // map, infoWindow and contentString
          bindInfoWindow(marker, map, infoWindow, html);
          markerClick(marker);

      }

  });

  // This function is outside the for loop.
  // When a marker is clicked it closes any currently open infowindows
  // Sets the content for the new marker with the content passed through
  // then it open the infoWindow with the new content on the marker that's clicked
  function bindInfoWindow(marker, map, infoWindow, html) {
      google.maps.event.addListener(marker, 'click', function () {
          infoWindow.close();
          infoWindow.setContent(html);
          infoWindow.open(map, marker);
      });
  }

  function markerClick(marker) {
      google.maps.event.addListener(marker, 'click', function () {
          sendClick(marker);
          map.panTo(marker.getPosition());
      });
  }

  function createUserMarker() {

        userMarker = new google.maps.Marker({
              position: null,
              map: map,
              title: "You",
          });

  }

  function dropUserMarker(userCoords) {

        userMarker.setPosition(userCoords);
        showMarkerWithAnimation(userMarker);

  }

// Autocomplete
  function addressAutocompleted() {
  var place = autocomplete.getPlace();
  if (place.geometry) {
    userCoords = place.geometry.location;
    map.panTo(userCoords);
    dropUserMarker(userCoords);
  }
}

// Update map center without autocomplete
  function updateMapCenter(evt) {
    var address = $('#address-entry').val();
    geocoder.geocode( { 'address': address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        userCoords = results[0].geometry.location;
        map.setCenter(userCoords);
        dropUserMarker(userCoords);
      } else {
        alert("Geocode was not successful for the following reason: " + status);
      }
    });
  }

// Update the map when filters change
  function updateMap() {
    console.log("got here");
    var one;

    for (one = 0; one < markerArray.length; one++) {
        markerArray[one].setVisible(true);
      }

    if (onlyShow["acceptVolunteers"]) {
      for (one = 0; one < markerArray.length; one++) {
        if (!markerArray[one].volunteers) {
          markerArray[one].setVisible(false);
        }
      }
    // } else {
    //   for (one = 0; one < markerArray.length; one++) {
    //     if (!markerArray[one].visible){
    //     // showMarkerWithAnimation(markerArray[one]);
    //     }
    //   }
    }

    for (one = 0; one < markerArray.length; one++) {
      for (var animal in onlyShow["animals"]) {
        // console.log(onlyShow["animals"][animal]);
        // console.log(markerArray[one].animals);
        if (($.inArray(onlyShow["animals"][animal],markerArray[one].animals)) < 0) {
          markerArray[one].setVisible(false);
        }
      }
  
  }
}

// Before hiding markers, animate their removal from the map
function removeMarkerWithAnimation(marker){
  marker.setAnimation(google.maps.Animation.BOUNCE);

  setTimeout(function(){
    marker.setAnimation(null);
    marker.setVisible(false);
     }, 720);

}

function showMarkerWithAnimation(marker){
  marker.setAnimation(google.maps.Animation.BOUNCE);
  marker.setVisible(true);

    setTimeout(function(){
      marker.setAnimation(null);
    }, 720);
}

// Update the showOnly object (filters) when any checkbox is checked/unchecked
  function updateFilters(evt) {
    console.log(this.id);
    var that = this;
    var thisFilter = this.id;

    if (thisFilter == "accepting-volunteers") {
      if($(this).is(':checked')){
        onlyShow["acceptVolunteers"] = true;
      } else {
        onlyShow["acceptVolunteers"] = false;
      }
    } else {
      if($(this).is(':checked')){
         onlyShow["animals"].push(thisFilter[0]);
      } else {
          var removeThis = onlyShow["animals"].indexOf(thisFilter[0]);
          if (removeThis > -1) {
              onlyShow["animals"].splice(removeThis, 1);
          }
      }

    }
      updateMap();
      console.log(onlyShow["animals"]);
      console.log(onlyShow["acceptVolunteers"]);

  }

  function returnClickSuccess(data) {
    console.log("SUCCESS");
  }

  function sendClick(marker) {
    console.log("WIN");
    var clickedOrg = marker.orgId;
    console.log(clickedOrg);
    var currentFilters = 'filters';

    if (onlyShow["acceptVolunteers"] === true) {
        currentFilters = currentFilters + '&volunteers';
    }

    for (var i = 0; i < onlyShow["animals"].length; i++) {
        currentFilters = currentFilters + '&' + onlyShow["animals"][i];
    }

    console.log(currentFilters);

        $.post('/_track-click', {
        'orgId': clickedOrg,
        'currentFilters': currentFilters
      }, returnClickSuccess);

  }

// Listen for changes to the filters / address bar
    $('.map-filter-cb').on("click", updateFilters);
    $('#submit-address').on("click", updateMapCenter);
    // autocomplete.addListener('place_changed', onPlaceChanged);

}



// google.maps.event.addDomListener(window, 'load', initMap);