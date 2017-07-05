'use strict';

const remote = require('electron').remote;
const {app} = remote;
const zerorpc = require("zerorpc")
const path = require('path')
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


function onServerReady() {
  let startButton = document.querySelector('#start-monitoring');
  if (currentPageName == "splash") {
    initializeSplash();
  } else if (currentPageName == "form1") {
    initializeForm1()
  } else if (currentPageName == "form2") {
    initializeForm2()
  } else if (currentPageName == "monitoring") {
    initializeMonitoring()
  }
}

function initializeSplash() {
  let startButton = document.querySelector('#start-monitoring');

  startButton.addEventListener('click', function(e) {
    e.preventDefault();
    loadNextPage("form1");
    onServerReady();
  });
}

function loadNextPage(pageName) {
  currentPageName = pageName;
  remote.getCurrentWindow().loadURL(require('url').format({
    pathname: path.join(__dirname, 'html/' + pageName + '.html'),
    protocol: 'file:',
    slashes: true
  }))
}

function initializeForm1() {
  let acceptForm = document.querySelector('#accept-form')
  let acceptValue = document.querySelector('#accept-value')
  let acceptResult = document.querySelector('#accept-result')

  client.invoke("accept", "", app.getPath('userData'), (error, res) => {
    if(error) {
      console.log(error)
    } else {
      acceptValue.value = res
      console.log("Existing accept value: " + res)
    }
  })

  acceptForm.addEventListener('submit', function(e) {
    e.preventDefault();
    client.invoke("accept", acceptValue.value, app.getPath('userData'), (error, res) => {
      if(error) {
        acceptResult.textContent = error
      } else {
        acceptResult.textContent = res;
        loadNextPage("form2");
      }
    })
  });
}

function initializeForm2() {
  let tokenForm = document.querySelector('#token-form')
  let tokenValue = document.querySelector('#token-value')
  let tokenResult = document.querySelector('#token-result')

  client.invoke("token", "", app.getPath('userData'), (error, res) => {
    if(error) {
      console.log(error)
    } else {
      tokenValue.value = res;
      console.log('Existing token: ' + res)
    }
  })

  tokenForm.addEventListener('submit', function(e) {
    e.preventDefault();
    client.invoke("token", tokenValue.value, app.getPath('userData'), (error, res) => {
      if(error) {
        tokenResult.textContent = error
      } else {
        tokenResult.textContent = res;
        loadNextPage("monitoring")
      }
    })
  });
}

function initializeMonitoring() {
  var isMonitoring = false;
  let monitorLink = document.querySelector('#monitor-link')
  let monitoringStatus = document.querySelector('#monitor-status')

  var ws = new WebSocket("ws://127.0.0.1:5678/");
  var status = document.getElementById('detected');
  ws.onmessage = function (event) {
    if (isMonitoring) {
      if (event.data == 'True') {
        status.innerHTML = 'Motion detected';
        status.style.opacity = 1;
      } else if (event.data == 'False') {
        status.innerHTML = 'No motion';
        status.style.opacity = 0.5;
      } else {
        status.innerHTML = event.data;
        status.style.opacity = 1;
      }
      console.log(event.data);
    }
  };

  monitorLink.addEventListener('click', function (e) {
    e.preventDefault();
    toggleMonitoring();
  });

  function toggleMonitoring() {
    isMonitoring = !isMonitoring;
    client.invoke("monitor", app.getPath('userData'), (error, res) => {
      if (error) {
        console.log(error)
      } else {
        monitorLink.textContent = res;
      }
    })
    if (isMonitoring) {
      monitoringStatus.innerHTML = 'Monitoring...'
    } else {
      monitoringStatus.innerHTML = 'Not monitoring'
      status.innerHTML = "(paused)";
      status.style.opacity = 0.5;
    }
  }

  toggleMonitoring();
}
