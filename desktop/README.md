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

![screen shot 2017-07-04 at 6 07 28 pm](https://user-images.githubusercontent.com/2068077/27845420-35d9e348-60e4-11e7-98b8-678f87ad2a74.png)
![screen shot 2017-07-04 at 6 07 36 pm](https://user-images.githubusercontent.com/2068077/27845417-35d66a7e-60e4-11e7-9786-e3e0be2dc05e.png)
![screen shot 2017-07-04 at 6 07 44 pm](https://user-images.githubusercontent.com/2068077/27845421-35dc051a-60e4-11e7-9899-44d506017347.png)
![screen shot 2017-07-04 at 6 07 50 pm](https://user-images.githubusercontent.com/2068077/27845418-35d77b76-60e4-11e7-853e-f5e7f4b5baee.png)
![screen shot 2017-07-04 at 6 10 26 pm](https://user-images.githubusercontent.com/2068077/27845419-35d81ee6-60e4-11e7-8b1b-3d4ec012e1d0.png)
