(function() {
    // The width and height of the captured photo. We will set the
    // width to the value defined here, but the height will be
    // calculated based on the aspect ratio of the input stream.
  
    var width = 640;    // We will scale the photo width to this
    var height = 0;     // This will be computed based on the input stream
  
    // |streaming| indicates whether or not we're currently streaming
    // video from the camera. Obviously, we start at false.
  
    var streaming = false;
  
    // The various HTML elements we need to configure or control. These
    // will be set by the startup() function.
  
    var video = null;
    var canvas = null;
    var startbutton = null;
    var uploadphoto = null;
    var facedetect = null;
    var facerecognized = null;
    var error = null;

    var imageCapture;
    var photoBlob;
  
    function startup() {
      video = document.getElementById('video');
      canvas = document.getElementById('canvas');
      photo = document.getElementById('photo');
      startbutton = document.getElementById('startbutton');
      uploadphoto = document.getElementById('uploadphoto');
      facedetect = document.getElementById('facedetect');
      facerecognized = document.getElementById('facerecognized');
      error = document.getElementById('error');
  
      navigator.mediaDevices.getUserMedia({video: true, audio: false}).then(function(stream) {
        video.srcObject = stream;
        const track = stream.getVideoTracks()[0];
        imageCapture = new ImageCapture(track);
        video.play();
      })
      .catch(function(err) {
        console.log("An error occurred: " + err);
      });
  
      video.addEventListener('canplay', function(ev){
        if (!streaming) {
          height = video.videoHeight / (video.videoWidth/width);
        
          // Firefox currently has a bug where the height can't be read from
          // the video, so we will make assumptions if this happens.
        
          if (isNaN(height)) {
            height = width / (4/3);
          }
        
          video.setAttribute('width', width);
          video.setAttribute('height', height);
          canvas.setAttribute('width', width);
          canvas.setAttribute('height', height);
          streaming = true;
        }
      }, false);
  
      startbutton.addEventListener('click', function(ev){
        takepicture();
        ev.preventDefault();
      }, false);

      uploadphoto.addEventListener('click', function(ev) {
          if (photoBlob) {
            upload_picture(photoBlob);
          }
        ev.preventDefault();
      }, false);

      facedetect.addEventListener('click', function(ev) {
        takepicture();
        if (photoBlob) {
          console.log("photo blob: ", photoBlob);
          recognize(photoBlob);
        }
        ev.preventDefault();
      }, false);
      
      clearphoto();
    }
  
    // Fill the photo with an indication that none has been
    // captured.
  
    function clearphoto() {
      var context = canvas.getContext('2d');
      context.fillStyle = "#AAA";
      context.fillRect(0, 0, canvas.width, canvas.height);
      photoBlob = null;
    }
  
    // take a still photo (blob)
    function takepicture() {
        if (width && height) {
            var tmp = document.getElementById('username');
            tmp.value = '';
            
            imageCapture.takePhoto().then(blob => {
            console.log("blob: ", blob);
            photoBlob = blob;
            
            var context = canvas.getContext('2d');
            // const canvas = document.querySelector('#canvas');
            canvas.width = width;
            canvas.height = height;
            context.drawImage(video, 0, 0, width, height);

            }).catch(error => console.error(error));
        } else {
            clearphoto();
        }
    }

    function recognize(blob) {
      let formData = new FormData();
      formData.append('file', blob);
      fetch('/find', {method:"POST", body: formData}).then(res => res.json()).then(data => {
        console.log(data);
      });
    }

    function upload_picture(blob) {
        let formData = new FormData();
        formData.append("file", blob);

        username = document.getElementById('username');
        console.log("on startup username: ", username.value);
        formData.append("name", username.value);
        

        fetch('/upload/image', {method: "POST", body: formData}).then(res => res.json()).then(data => {
          console.log(data);
          if (!data.hasOwnProperty('success')) {
            error.innerHTML = data['message'];
          } 
          clearphoto();
        }).catch(error => {
            console.error(error);
        });
    }
  
    // Set up our event listener to run the startup process
    // once loading is complete.
    window.addEventListener('load', (ev) => { console.log("htmlloaded", document); startup(); });
  })();