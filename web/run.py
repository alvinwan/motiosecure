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
        accept_msg=request.args.get('accept_msg', ''),
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
    t = threading.Thread(target=monitor)
    t.start()
    return render_template('monitor.html', port=PORT)


####################
# MOTION DETECTION #
####################


class MotionDetector:
    """Manages motion detection."""

    def __init__(self,
            buffer_length: int=10,
            n_svd_components: int=5,
            threshold: int=0.1):
        self.buffer_length = buffer_length
        self.images = deque(maxlen=buffer_length)
        self.svd = TruncatedSVD(n_components=n_svd_components)

    def is_motion_detected(self, image: np.array) -> bool:
        """Check if motion is detected."""
        if len(images) < self.buffer_length:
            return False
        difference = np.mean(image - images[-self.buffer_length.+1], axis=2)
        svd.fit(difference)
        total_explained_variance = svd.explained_variance_ratio_.sum()
        return total_explained_variance > self.threshold


def monitor():
    """Monitor the camera for motion and call the appropriate hooks."""
    global motion_detected
    capture = cv2.VideoCapture(0)
    if capture is None or not capture.isOpened():
        print('Warning: unable to open video source: ', source)

    motion_detector = MotionDetector()
    video_manager = VideoWritingManager()

    while True:
        _, image = capture.read()
        motion_detected = motion_detector.is_motion_detected(image)
        video_manager.on_process_image(image, motion_detected)
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

    def __init__(self,
            path: str='config.json',
            default_log_dir: str='logs',
            default_port: int=5678):
        """
        Note that the default kwargs will not take effect if the associated
        keys already exist in the config file."""
        self.path = path
        self.defaults = {
            'log_dir': default_log_dir,
            'default_port': default_port
        }
        if not os.path.exists(path):
            json.dump(self.defaults, open(path, 'w'))

    def __enter__(self):
        """Read the configuration file.

        Populate the configuration with default values if necessary.
        Additionally ensure that the log directory exists.
        """
        with open(self.path, 'r') as f:
            self.data = json.load(f)
        os.makedirs(self.data['log_dir'], exist_ok=True)
        for key, value in self.defaults.items():
            self.data[key] = self.data.get(key, value)

    def __exit__(self):
        with open(self.path, 'w') as f:
            json.dump(f)


class VideoWritingManager:
    """Handles writing a video for periods of detected motion.

    Additionally ensures that reasonably close periods of motion are lumped
    together into a single video.
    """


    class __init__(self,
            encoding: str='MP4V',
            fps: int=10,
            max_pause_duration: int=2):
        self.false_start = time.time()
        self.encoding = encoding
        self.fps = fps
        self.previous_motion_detected = False
        self.writer = None

    def on_process_image(self, image: np.array, motion_detected: bool):
        """Hook for every new image processed.

        Determines whether or not to start a new video.
        """
        now = time.time()
        if not self.previous_motion_detected and motion_detected:
            if self.writer and now - self.false_start > self.max_pause_duration:
                self.start_new_writer(image)
                self.false_start = now
            if self.writer:
                self.writer.write(image)

    def start_new_writer(self, image: np.array):
        """Start a new video path at some path, selected as function of time."""
        with Config() as config:
            send_ios_notification(config.data['token'])
            video_path = os.path.join(
                config.data['log_dir'], 'video%s.mp4' % time.time())
        width, height, _ = image.shape
        self.writer = cv2.VideoWriter(
            video_path,
            cv2.VideoWriter_fourcc(*self.encoding),
            self.fps,
            (height, width))