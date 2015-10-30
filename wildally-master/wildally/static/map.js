

var map;

function initMap() {
  map = new google.maps.Map(document.getElementById('main-map'), {
    center: {lat: 47.29247, lng: -120.39987},
    zoom: 7
  });


var infoWindow = new google.maps.InfoWindow({
      width: 250
  });

  // Retrieving the information with AJAX
  $.get('/orgs.json', function (orgs) {

      var org, marker, html;

      for (var key in orgs) {
          org = orgs[key];

          // Define the marker
          marker = new google.maps.Marker({
              position: new google.maps.LatLng(org.latitude, org.longitude),
              map: map,
              animation: google.maps.Animation.DROP,
              title: org.orgName
          });

          var printAddress;

          if (org.address1) {
              if (org.address2) {
                  printAddress = org.address1 + '<br />' + org.address2;
              } else {
                  printAddress = org.address1 + '<br />'; }
          } else { printAddress = 'This is an approximate location. Please call for directions. <br />'; }

          // Define the content of the infoWindow
          html = (
              '<div class="window-content">' +
                  '<h3>' + org.orgName + '</h3>' +
                  '<h5>' + org.phone + '</h5>' +
                  '<p>' + printAddress +
                        org.city + ', ' +
                        org.state + ' ' +
                        org.zipcode +
                  '</p>' + '<p>' + org.desc + '</p></div>');

          // Inside the loop we call bindInfoWindow passing it the marker,
          // map, infoWindow and contentString
          bindInfoWindow(marker, map, infoWindow, html);
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
}

// google.maps.event.addDomListener(window, 'load', initMap);