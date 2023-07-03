
const bucketName = "photo-image-bucket-2";
const apiKey = "PUT-IN-API-KEY-HERE";
const apiEndPoint = "https://4bai8kyq56.execute-api.us-east-1.amazonaws.com/v1";

window.onload = function() {
  var sendbtn = document.getElementById('submit');
  var sendqbtn = document.getElementById('submitq');
  var image_display = document.getElementById('image_display');
  sendbtn.onclick = function() {
      var input = $("#fileupload").val();
      var fileInput = document.getElementById("fileupload");
      var customLabels = $("#customlabels").val();
      customLabels = customLabels.trim();
      console.log(input)
      console.log(customLabels)
      console.log('uploading file.....')

      var file = fileInput.files[0]; // files is a FileList object (similar to NodeList)
      console.log(file)

      url = apiEndPoint + "/upload/" + bucketName + "/" + file.name
      putStuff(url, file, customLabels)
      $("#fileupload").val('') // cleanup fileupload field
      $("#customlabels").val('') // cleanup customlabels field
  }


  sendqbtn.onclick = function() {
      var input = $("#q").val();
      // TODO FMugisho - clean up the search bar here
      console.log(input)
      console.log('processing your input')
      $("#q").val('') // cleaning up query space

      var apigClient = apigClientFactory.newClient({
          apiKey: apiKey
      });
      var params = {
          //This is where any header, path, or querystring request params go. The key is the parameter named as defined in the API
          "q": input
      };
      var body = {
          //This is where you define the body of the request
      };
      var additionalParams = {
          //If there are any unmodeled query parameters or headers that need to be sent with the request you can add them here
          headers: {

          },
          queryParams: {

          }
      };

      apigClient.searchGet(params, body, additionalParams)
          .then(function(result) {
              //This is where you would put a success callback
              image_display.innerHTML = '';
              images = result.data.results[0].url
              console.log("hey hey")
              console.log(Object.keys(images).length > 0);
              if (Object.keys(images).length > 0){
                // display all matching results.
                image_display.innerHTML += 'Success! Here is the query result(s): <br>';
                for (const [key, value] of Object.entries(images)) {
                  image_display.innerHTML += '<img src=' + value + '> <br>';
                }

              } else {
                // there are no matching results and we should communicate that to the user.
                image_display.innerHTML += 'Sorry, there are no matching images!';
              }

          }).catch(function(result) {
              //This is where you would put an error callback
          });


  }

}

/* runSpeechRecognition function */
function runSpeechRecognition() {
  var transcript;
  // get output div reference
  var output = document.getElementById("output");
  // get action element reference
  var action = document.getElementById("action");
  // new speech recognition object
  var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
  var recognition = new SpeechRecognition();

  // This runs when the speech recognition service starts
  recognition.onstart = function() {
  };

  recognition.onspeechend = function() {
      recognition.stop();
  }

  // This runs when the speech recognition service returns result
  recognition.onresult = function(event) {
      var q = document.getElementById("q"); // addition
      transcript = event.results[0][0].transcript;
      q.value = transcript;
      output.classList.remove("hide");
  };

  // start recognition
  recognition.start();
  return transcript
}

async function putStuff(url, file, customLabels){  
  try {
    const response = await fetch(url, {
      method: "PUT",
      headers: {
        "Content-Type": file.type,
        "x-amz-meta-customLabels": customLabels
      },
      body: file
    });
    if (!response.ok) {
      const message = 'Error with Status Code: ' + response.status;
      throw new Error(message);
    }
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.log('Error: ' + error);
  }
}