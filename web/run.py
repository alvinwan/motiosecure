from apns import APNs
from apns import Frame
from apns import Payload
from flask import request
from flask import abort
from subprocess import call
from flask import Flask
from flask import url_for
from flask import redirect
from sklearn.decomposition import TruncatedSVD
from collections import deque

import cv2
import numpy as np
import time
import threading
import websockets
import asyncio
import datetime
import time
import random
import os
import os.path
import json

app = Flask(__name__)

motion_detected = False
autoaccept_key = random.getrandbits(128)
DEQUE_LENGTH = 10
THRESHOLD = 0.1
LOG_DIR = 'logs/%s' % random.randint(10000, 99999)
MAX_FALSE_DURATION = 2  # maximum duration between periods of motion detection, for videos to be strung together (in seconds)
PORT = 6789

if not os.path.exists(CONFIG_PATH):
    json.dump({}, open(CONFIG_PATH, 'w'))
os.makedirs(LOG_DIR, exist_ok=True)


@app.route("/")
def index():
    autoaccept_msg = request.args.get('autoaccept_msg', '')
    token_msg = request.args.get('token_msg', '')
    return '<p>1. To view live feeds, add your phone number or email</p><span>For phone numbers, add your country code. For the US, use +1<phone number>.</span>%s<form method="post" action="/autoaccept"><input type="text" name="value" placeholder="+18880008888 or wallawallabingbang@gmail.com"><input type="hidden" name="key" value="%s"><input type="submit"></form><p>2. Download the iOS app, and enter token displayed on the app homepage, below:</p>%s<form action="/token" method="post"><input type="text" name="token"><input type="hidden" name="key" value="%s"><input type="submit"></form><p>3. <a href="%s">Start monitoring"</a></p>' % (autoaccept_msg, autoaccept_key, token_msg, autoaccept_key, url_for('monitor'))


@app.route("/autoaccept", methods=['POST'])
def accept():
    global autoaccept_key
    if request.remote_addr != '127.0.0.1' or \
            int(request.form['key']) != autoaccept_key:
        abort(403)
    call('defaults write com.apple.FaceTime AutoAcceptInvitesFrom -array-add'.split(' ') + [request.form['value']])
    with Config() as config:
        if 'autoaccept' not in config.data:
            config.data['autoaccept'] = []
        config.data['autoaccept'].append(request.form['token'])
    autoaccept_key = random.getrandbits(128)
    return redirect(url_for('index', autoaccept_msg='Successfully added' + request.form['value']))


@app.route("/token", methods=['POST'])
def token():
    global autoaccept_key
    if request.remote_addr != '127.0.0.1' or \
            int(request.form['key']) != autoaccept_key:
        abort(403)
    with Config() as config:
        config.data['token'] = request.form['token']
    autoaccept_key = random.getrandbits(128)
    return redirect(url_for('index', token_msg='Successfully added token:' + request.form['token']))


@app.route("/monitor")
def monitor():
    t = threading.Thread(target=watch)
    t.start()
    return """
    <!DOCTYPE html>
<html>
    <head>
        <title>WebSocket demo</title>
    </head>
    <body>
        <p>Monitoring started
        <ul>
            <li>Motion Detected: <span id="detected"></span></li>
        </ul>
        <script>
            window.onload = function() {
                var ws = new WebSocket("ws://127.0.0.1:%d/");
                var status = document.getElementById('detected');
                ws.onmessage = function (event) {
                    status.innerHTML = event.data;
                    console.log(event.data);
                };
            }
        </script>
    </body>
</html>
""" % PORT


def watch():
    global motion_detected
    capture = cv2.VideoCapture(0)
    if capture is None or not capture.isOpened():
        print('Warning: unable to open video source: ', source)

    images = deque(maxlen=DEQUE_LENGTH)
    svd = TruncatedSVD(n_components=5)
    writer = None
    false_start = time.time()

    config = json.load(open(CONFIG_PATH, 'r'))

    while True:
        _, image = capture.read()
        if len(images) > DEQUE_LENGTH - 1:
            difference = np.mean(image - images[-DEQUE_LENGTH+1], axis=2)
            svd.fit(difference)
            total_explained_variance = svd.explained_variance_ratio_.sum()
            previous_motion_detected = motion_detected
            motion_detected = total_explained_variance > THRESHOLD
            if not previous_motion_detected and motion_detected:
                now = time.time()
                if writer and now - false_start > MAX_FALSE_DURATION:
                    writer.release()
                    new_video = True
                elif writer:
                    new_video = False
                else:
                    new_video = True

                if new_video:
                    send_ios_notification(config['token'])
                    video_path = os.path.join(LOG_DIR, 'video%s.mp4' % time.time())
                    width, height, _ = image.shape
                    writer = cv2.VideoWriter(
                        video_path,
                        cv2.VideoWriter_fourcc(*'MP4V'),
                        10,
                        (height, width))
            if writer:
                writer.write(image)
            if previous_motion_detected and not motion_detected and writer:
                false_start = time.time()
        images.append(image)

def start_socket():
    start_server = websockets.serve(send_detections, '127.0.0.1', PORT)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


async def send_detections(websocket, path):
    global motion_detected
    while True:
        await websocket.send(str(motion_detected))
        await asyncio.sleep(0.1)


def send_ios_notification(token: str):
    apns = APNs(use_sandbox=True, cert_file='bundle.pem', key_file='bundle.pem')

    # Send a notification
    payload = Payload(
        alert="Motion detected", sound="default", badge=1, mutable_content=True)
    apns.gateway_server.send_notification(token, payload)

t = threading.Thread(target=start_socket)
t.start()


class Config:
    """Configuration class.

    Makes reading and writing from config slightly easier. Simple treat the
    config object using a with statement.

    with Config() as config:
        config.data['key'] = 'some value'
    """

    DEFAULT_PATH = 'config.json'

    def __init__(self, path: str=DEFAULT_PATH):
        self.path = path

    def __enter__(self):
        with open(self.path, 'r') as f:
            self.data = json.load(f)

    def __exit__(self):
        with open(self.path, 'w') as f:
            json.dump(f)
