const {app} = require('electron').remote;
const zerorpc = require("zerorpc")
let client = new zerorpc.Client()

client.connect("tcp://127.0.0.1:4242")

client.invoke("onstart", app.getPath('userData'), (error, res) => {
  if(error || res !== 'server ready') {
    console.error(error)
  } else {
    console.log("server is ready")
    onServerReady()
  }
})

let acceptForm = document.querySelector('#accept-form')
let acceptValue = document.querySelector('#accept-value')
let acceptResult = document.querySelector('#accept-result')
let tokenForm = document.querySelector('#token-form')
let tokenValue = document.querySelector('#token-value')
let tokenResult = document.querySelector('#token-result')
let monitorLink = document.querySelector('#monitor-link')


function onServerReady() {

  client.invoke("token", "", app.getPath('userData'), (error, res) => {
    if(error) {
      console.log(error)
    } else {
      tokenValue.value = res
    }
  })

  client.invoke("accept", "", app.getPath('userData'), (error, res) => {
    if(error) {
      console.log(error)
    } else {
      acceptValue.value = res
    }
  })

  var ws = new WebSocket("ws://127.0.0.1:5678/");
  var status = document.getElementById('detected');
  var originalClassName = status.className;
  ws.onmessage = function (event) {
      if (event.data == 'True') {
        status.innerHTML = 'motion detected';
        status.className = originalClassName;
      } else if (event.data == 'False') {
        status.innerHTML = 'No motion detected';
        status.className = originalClassName + ' inactive';
      } else {
        status.innerHTML = event.data;
        status.className = originalClassName + ' inactive';
      }
      console.log(event.data);
  };
}


acceptForm.addEventListener('submit', function(e) {
  e.preventDefault();
  client.invoke("accept", acceptValue.value, app.getPath('userData'), (error, res) => {
    if(error) {
      acceptResult.textContent = error
    } else {
      acceptResult.textContent = res
    }
  })
});

tokenForm.addEventListener('submit', app.getPath('userData'), function(e) {
  e.preventDefault();
  client.invoke("token", tokenValue.value, (error, res) => {
    if(error) {
      tokenResult.textContent = error
    } else {
      tokenResult.textContent = res
    }
  })
});

monitorLink.addEventListener('click', function (e) {
  e.preventDefault();
  client.invoke("monitor", app.getPath('userData'), (error, res) => {
    if (error) {
      console.log(error)
    } else {
      monitorLink.textContent = res;
    }
  })
})
