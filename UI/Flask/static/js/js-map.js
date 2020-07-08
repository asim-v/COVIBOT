class GoogleMap {
  constructor(el) {
    this.element = el;
    this.options = {
      disableDefaultUI: true,
      draggable: true,
      disableDoubleClickZoom: true,
      keyboardShortcuts: true,
      zoomControl: true,
      scrollwheel: true,
      keyboardShortcuts: true,
      backgroundColor: '#f8f8f8',
      zoom: 10,
      center: new google.maps.LatLng(53.728235, -0.409730),
      styles: [
      {
        "featureType": "landscape",
        "elementType": "geometry",
        "stylers": [{
          "color": "#ffffff" }] },


      {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [{
          "color": "#e3e3e3" }] },


      {
        "elementType": "labels.text",
        "stylers": [{
          "visibility": "off" }] },


      {
        "elementType": "labels.icon",
        "stylers": [{
          "visibility": "off" }] },


      {
        "featureType": "all",
        "elementType": "labels.icon",
        "stylers": [{
          "visibility": "off" }] },


      {
        "featureType": "poi",
        "elementType": "geometry",
        "stylers": [{
          "color": "#dddddd" }] },


      {
        "featureType": "road.highway",
        "elementType": "geometry.fill",
        "stylers": [{
          "color": "#cccccc" }] },


      {
        "featureType": "road.highway",
        "elementType": "geometry.stroke",
        "stylers": [{
          "visibility": "off" }] },


      {
        "featureType": "road.arterial",
        "elementType": "geometry",
        "stylers": [{
          "color": "#dddddd" }] },


      {
        "featureType": "road.local",
        "elementType": "geometry",
        "stylers": [{
          "color": "#ffffff" }] },


      {
        "featureType": "transit",
        "elementType": "geometry",
        "stylers": [{
          "visibility": "off" }] }] };




  }

  init() {
    const map = new google.maps.Map(this.element, this.options);

    const icon = {
      url: '',
      anchor: new google.maps.Point(50, 50),
      scaledSize: new google.maps.Size(50, 50) };


    const marker = new google.maps.Marker({
      position: new google.maps.LatLng(53.728235, -0.409730),
      map: map,
      icon: icon,
      title: 'Click me!' });


    const info = new google.maps.InfoWindow({
      content: `<div>
                  <p>Hi there!</p>
                </div>` });


    marker.addListener('click', () => {
      info.open(map, marker);
    });
  }}


// Create a new instance of the GoogleMap class
const map = new GoogleMap(document.querySelector('.map'));

// Initialise the GoogleMap class when Google Maps has loaded
google.maps.event.addDomListener(window, 'load', () => map.init());