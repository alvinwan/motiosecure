# MotioSecure Web Application

> This project was created for Python3.6. Since the project uses typecasting, it does not support Python2. Since it uses async syntax, it does not support older Python3.x versions either.

Navigate to the `web/` directory if you haven't already, and install all Python dependencies.

```
pip install -r requirements.txt
```

To launch, just run the Python file from this directory.

```
FLASK_APP=run.py flask run
```

# How it Works

We use `Flask` for the application. On server-side, `opencv` abstracts away the camera. We compute the difference across `l` timesteps and use `scipy`'s `SVD` to analyze explained variance ratios. If the sum of the top `k` ratios exceed a threshold, we consider motion to be detected.

`opencv` provides additional utilities that allow us to encode and write to mp4 videos. A Python interface for Apple's Push Notification Service `pyapns` allows the Python app to interface with iOS notifications accordingly. A third-party library `websockets` is used to launch a local socket, giving the web application live updates for "motion detected" or not.

# Development

*Installation is no different from the instructions provided above.*

![screen shot 2017-06-25 at 10 16 27 pm](https://user-images.githubusercontent.com/2068077/27526565-ada50ab4-59fb-11e7-90ce-f63655251f4f.png)
![screen shot 2017-06-25 at 10 16 36 pm](https://user-images.githubusercontent.com/2068077/27526566-ae9b2b2e-59fb-11e7-81d3-1911b7dda2ef.png)
