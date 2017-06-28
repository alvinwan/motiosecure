# MotioSecure
Simple security platform with motion detection implementation for cheap, low-quality camera lens

**Mac and iOS apps are coming soon**

Ever have a friend hijack your computer while you're away? Ever wanted to catch them red-handed? Run this application to do just that. With just an iOS app and a mac app, you'll be good to go. **Applications are pending review. Want it now? See Development installation instructions below.**

- Sends a notification to your phone when motion is detected
- Saves all detected motion as mp4 videos for playback
- Surprise the intruder with a live camera feed, and engage with your invader in conversation!
- Uses Apple security protocols to make live feed, notifications available; no janky, inter-device, unencrypted communication

> This is not a serious security platform. For all intents and purposes, I wrote it to prank my friends. With that said, the application actually does what I claim above. I make no guarantees about its ability to prevent theft or its security. Please don't use this seriously.

# Development

Launch the `iOS` directory in XCode. Change the bundle ID and follow installation instructions in the iOS README [`ios/README.md`](https://github.com/alvinwan/motiosecure/tree/master/ios).

Second, navigate to the `web/` directory and install all Python dependencies.

```
cd web/
pip install -r requirements.txt
```

To run, again from the `web/` directory, enter the following.

```
FLASK_APP=run.py flask run
```

![screen shot 2017-06-25 at 10 16 27 pm](https://user-images.githubusercontent.com/2068077/27526565-ada50ab4-59fb-11e7-90ce-f63655251f4f.png)
![screen shot 2017-06-25 at 10 16 36 pm](https://user-images.githubusercontent.com/2068077/27526566-ae9b2b2e-59fb-11e7-81d3-1911b7dda2ef.png)
