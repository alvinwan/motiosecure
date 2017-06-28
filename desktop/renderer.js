const zerorpc = require("zerorpc")
let client = new zerorpc.Client()

client.connect("tcp://127.0.0.1:4242")

client.invoke("echo", "server ready", (error, res) => {
  if(error || res !== 'server ready') {
    console.error(error)
  } else {
    console.log("server is ready")
  }
})

let acceptSubmit = document.querySelector('#accept-submit')
let tokenSubmit = document.querySelector('#token-submit')
let monitorLink = document.querySelector('#monitor-link')

acceptSubmit.addEventListener('onclick', () => {
  
});
