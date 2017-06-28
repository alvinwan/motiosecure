# MotioSecure Desktop Application

**Coming soon: Install from the Mac app store**

# Development

We expose several Python endpoints through zmq, with `zerorpc`:

- `accept`: Added contact information to the computer's auto-accept list.
- `token`: Save device-specific apns token for push notifications.
- `monitor`: Start and stop monitoring.

The electron app runs a Python subprocess and calls these endpoints accordingly,
using zerorpc. The monitoring app separately opens a websocket so that the electron frontend can communicate directly with the Python script.

For more information, see [Fleeting Year's example](https://github.com/fyears/electron-python-example), which this project is based on.

![screen shot 2017-06-28 at 1 01 23 am](https://user-images.githubusercontent.com/2068077/27626564-6536aadc-5b9d-11e7-8eaf-4f527ef77ad0.png)
![screen shot 2017-06-28 at 1 01 25 am](https://user-images.githubusercontent.com/2068077/27626565-653a67da-5b9d-11e7-8b40-5984bb5f0315.png)
