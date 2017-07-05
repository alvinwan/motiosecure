![mockup](https://user-images.githubusercontent.com/2068077/27844312-bb4019f4-60d4-11e7-95b6-11abaac2690f.png)


# MotioSecure
Simple security platform with motion detection implementation for cheap, low-quality camera lens

**Mac and iOS apps are coming soon**

Ever have a friend hijack your computer while you're away? Ever wanted to catch them red-handed? Run this application to do just that. With just an iOS app and a mac app, you'll be good to go. **Applications are pending review. Want it now? See Development installation instructions below.**

- Sends a notification to your phone when motion is detected
- Saves all detected motion as mp4 videos for playback
- Surprise the intruder with a live camera feed, and engage with your invader in conversation!
- Uses Apple security protocols to make live feed, notifications available; no janky, inter-device, unencrypted communication

> This is not a serious security platform. For all intents and purposes, I wrote it to prank my friends. With that said, the application actually does what I claim above. I make no guarantees about its ability to prevent theft or its security. Please don't use this seriously.

# How it Works

On server-side, `opencv` abstracts away the camera. We compute the difference across `l` timesteps and use `scipy`'s `SVD` to analyze explained variance ratios. If the sum of the top `k` ratios exceed a threshold, we consider motion to be detected.

`opencv` provides additional utilities that allow us to encode and write to mp4 videos. A Python interface for Apple's Push Notification Service `pyapns` allows the Python app to interface with iOS notifications accordingly. A third-party library `websockets` is used to launch a local socket, giving the application live updates for "motion detected" or not.

- See the [`web/` README](http://github.com/alvinwan/motiosecure/tree/master/web) for more on a locally-hosted web application.
- See the [`desktop/` README](http://github.com/alvinwan/motiosecure/tree/master/desktop) for how we packaged the application for Mac App Store distribution.
- See the [`ios/` README](http://github.com/alvinwan/motiosecure/tree/master/ios) for the mobile component.

![screen shot 2017-07-04 at 6 07 28 pm](https://user-images.githubusercontent.com/2068077/27845420-35d9e348-60e4-11e7-98b8-678f87ad2a74.png)
![screen shot 2017-07-04 at 6 07 36 pm](https://user-images.githubusercontent.com/2068077/27845417-35d66a7e-60e4-11e7-9786-e3e0be2dc05e.png)
![screen shot 2017-07-04 at 6 07 44 pm](https://user-images.githubusercontent.com/2068077/27845421-35dc051a-60e4-11e7-9899-44d506017347.png)
![screen shot 2017-07-04 at 6 07 50 pm](https://user-images.githubusercontent.com/2068077/27845418-35d77b76-60e4-11e7-853e-f5e7f4b5baee.png)
![screen shot 2017-07-04 at 6 10 26 pm](https://user-images.githubusercontent.com/2068077/27845419-35d81ee6-60e4-11e7-8b1b-3d4ec012e1d0.png)
