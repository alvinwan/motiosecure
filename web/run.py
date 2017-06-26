from apns import APNs
from apns import Frame
from apns import Payload
from flask import request
from flask import abort
from flask import render_template as flask_render_template
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
__safety_key = random.getrandbits(128)
__used_safety_keys = {}
DEQUE_LENGTH = 10
THRESHOLD = 0.1
LOG_DIR = 'logs/%s' % random.randint(10000, 99999)
MAX_FALSE_DURATION = 2  # maximum duration between periods of motion detection, for videos to be strung together (in seconds)
PORT = 6789

os.makedirs(LOG_DIR, exist_ok=True)

################
# CUSTOM HOOKS #
################


@app.before_request
def filter_post_requests():
    """Rudimentary checks for valid POST requests. ~Don't depend on this!~

    1) Checks that the IP address is localhost. (Note: this can be spoofed)
    2) Checks that the safety key is consistent with the last generated.
    """
    global __safety_key
    if request.method == 'POST': and (
            request.remote_addr != '127.0.0.1' or \
            int(request.form['__safety_key']) != __safety_key):
        abort(403)
    __used_safety_keys.add(__safety_key)


@app.after_request
def regenerate_safety_key():
    """
    Generate a new safety key after each request to prevent network spies
    from reusing safety keys.
    """
    global __safety_key
    __safety_key = random.getrandbits(128)


def render_template(template_name: str, **kwargs):
    """Add the current safety key for template rendering."""
    kwargs['__safety_key'] = __safety_key
    return flask_render_template(template_name, **kwargs)


#############
# WEB VIEWS #
#############


@app.route("/")
def index():
    return render_template(
        'index.html',
        autoaccept_msg=request.args.get('accept_msg', ''),
        token_msg=request.args.get('token_msg', ''))


@app.route("/accept", methods=['POST'])
def accept():
    """Add new contact to list of 'Facetime auto-accept' whitelist."""
    call('defaults write com.apple.FaceTime AutoAcceptInvitesFrom -array-add'.split(' ') + [request.form['value']])
    with Config() as config:
        if 'accept' not in config.data:
            config.data['accept'] = []
        config.data['accept'].append(request.form['token'])
    return redirect(url_for('index', autoaccept_msg='Successfully added' + request.form['value']))


@app.route("/token", methods=['POST'])
def token():
    """Set device-specific token as current app's target for notifications."""
    with Config() as config:
        config.data['token'] = request.form['token']
    return redirect(url_for('index', token_msg='Successfully added token:' + request.form['token']))


@app.route("/monitor")
def monitor():
    t = threading.Thread(target=watch)
    t.start()
    return render_template('monitor.html', port=PORT)


####################
# MOTION DETECTION #
####################

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
    """Launch new socket to provide live motion updates to web interface."""
    start_server = websockets.serve(send_detections, '127.0.0.1', PORT)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


async def send_detections(websocket, path):
    """Sends latest status update to web interface, through socket."""
    global motion_detected
    while True:
        await websocket.send(str(motion_detected))
        await asyncio.sleep(0.1)


def send_ios_notification(token: str):
    """Sends 'motion detected' notification to iOS device."""
    apns = APNs(use_sandbox=True, cert_file='bundle.pem', key_file='bundle.pem')

    # Send a notification
    payload = Payload(
        alert="Motion detected", sound="default", badge=1, mutable_content=True)
    apns.gateway_server.send_notification(token, payload)

t = threading.Thread(target=start_socket)
t.start()


#############
# UTILITIES #
#############


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
        if not os.path.exists(path):
            json.dump({}, open(path, 'w'))

    def __enter__(self):
        with open(self.path, 'r') as f:
            self.data = json.load(f)

    def __exit__(self):
        with open(self.path, 'w') as f:
            json.dump(f)
