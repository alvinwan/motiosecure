const zerorpc = require("zerorpc")
let client = new zerorpc.Client()

client.connect("tcp://127.0.0.1:4242")

client.invoke("echo", "server ready", (error, res) => {
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
// let monitorLink = document.querySelector('#monitor-link')


function onServerReady() {

  client.invoke("token", "", (error, res) => {
    if(error) {
      console.log(error)
    } else {
      tokenValue.value = res
    }
  })

  client.invoke("accept", "", (error, res) => {
    if(error) {
      console.log(error)
    } else {
      acceptValue.value = res
    }
  })
}


acceptForm.addEventListener('submit', function(e) {
  e.preventDefault();
  client.invoke("accept", acceptValue.value, (error, res) => {
    if(error) {
      acceptResult.textContent = error
    } else {
      acceptResult.textContent = res
    }
  })
});



tokenForm.addEventListener('submit', function(e) {
  e.preventDefault();
  client.invoke("token", tokenValue.value, (error, res) => {
    if(error) {
      tokenResult.textContent = error
    } else {
      tokenResult.textContent = res
    }
  })
});
