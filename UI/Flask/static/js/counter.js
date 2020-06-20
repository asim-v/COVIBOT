  // Your web app's Firebase configuration
  var firebaseConfig = {
    apiKey: "AIzaSyDVpxOSaZH08jzKvQJhssW06sloEHz5voc",
    authDomain: "colabotz.firebaseapp.com",
    databaseURL: "https://colabotz.firebaseio.com",
    projectId: "colabotz",
    storageBucket: "colabotz.appspot.com",
    messagingSenderId: "406791360909",
    appId: "1:406791360909:web:056f177e88849eb86eadc4",
    measurementId: "G-SJZ8WDR62E"
  };
  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);
  firebase.analytics();

  // Get a reference to the database service
  var database = firebase.database();