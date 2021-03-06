from apns import APNs
from apns import Frame
from apns import Payload
from subprocess import call
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
import zerorpc
import sys


motion_detected = False


class MotioSecureApi:

    num_monitor_threads = 0
    should_stop_thread = False
    socket_started = False

    def accept(self, contact: str, fs_dir: str):
        """Add contact information to auto-accept whitelist.

        :param contact: Phone number preceded by country code or email address
                        associated with an iCloud account. Leave empty to get
                        first contact.
        """
        with Config(fs_dir) as config:
            if not contact:
                return config.get('accept', [''])[0]
            if 'accept' not in config:
                config['accept'] = []
            if contact not in config['accept']:
                config['accept'].append(contact)
                call('defaults write com.apple.FaceTime AutoAcceptInvitesFrom -array-add'.split(' ') + [contact])
            else:
                return 'Contact already added.'
        return 'Successfully added contact'

    def token(self, token: str, fs_dir: str):
        """Add new mobile device token to configuration.

        :param token: String hex code taken from the iOS application. Leave
                      empty to get token.
        """
        with Config(fs_dir) as config:
            if not token:
                return config['token']
            config['token'] = token
        return 'Successfully set token'

    def monitor(self, fs_dir: str, exe_path: str):
        if MotioSecureApi.num_monitor_threads == 0:
            MotioSecureApi.should_stop_thread = False
            threading.Thread(target=monitor, args=(fs_dir, exe_path)).start()
            MotioSecureApi.num_monitor_threads += 1
            return 'Stop monitoring'
        else:
            MotioSecureApi.should_stop_thread = True
            return 'Start monitoring'

    def onstart(self, fs_dir: str) -> str:
        if not MotioSecureApi.socket_started:
            MotioSecureApi.socket_started = True
            threading.Thread(target=start_socket, args=(fs_dir,)).start()
        return "server ready"


def main():
    s = zerorpc.Server(MotioSecureApi())
    s.bind('tcp://127.0.0.1:4242')
    print('* [Info] Start running zmq on 4242')
    s.run()


# The following was taken from the `web/` interface. This code should mirror
# those files accordingly.


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
        self.threshold = threshold

    def is_motion_detected(self, image: np.array) -> bool:
        """Check if motion is detected."""
        self.images.append(image)
        if len(self.images) < self.buffer_length:
            return False
        difference = np.mean(image - self.images[-self.buffer_length+1], axis=2)
        self.svd.fit(difference)
        total_explained_variance = self.svd.explained_variance_ratio_.sum()
        return total_explained_variance > self.threshold


def monitor(fs_dir: str, exe_path: str):
    """Monitor the camera for motion and call the appropriate hooks."""
    global motion_detected
    capture = cv2.VideoCapture(0)
    if capture is None or not capture.isOpened():
        print('Warning: unable to open video source: ', source)

    motion_detector = MotionDetector()
    video_manager = VideoWritingManager(fs_dir, exe_path=exe_path)

    while True:
        _, image = capture.read()
        motion_detected = motion_detector.is_motion_detected(image)
        video_manager.on_process_image(image, motion_detected)

        if MotioSecureApi.should_stop_thread:
            MotioSecureApi.num_monitor_threads -= 1
            print('* [Info] Stopping monitor...')
            break


def start_socket(fs_dir: str):
    """Launch new socket to provide live motion updates to web interface."""
    with Config(fs_dir) as config:
        start_server = websockets.serve(
            send_detections, '127.0.0.1', config['port'])

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


def send_ios_notification(token: str, fs_dir: str, exe_path: str):
    """Sends 'motion detected' notification to iOS device."""
    print(' * [Info] Attempting to send iOS notification...')
    pem_path = 'bundle.pem'
    if 'MacOS/Electron' not in exe_path:
        pem_path = exe_path.replace('MacOS/MotioSecure', os.path.join(
        'Resources', 'app', 'bundle.pem'))
    apns = APNs(
        use_sandbox=True,
        cert_file=pem_path,
        key_file=pem_path)

    # Send a notification
    payload = Payload(
        alert="Motion detected", sound="default", badge=1, mutable_content=True)
    apns.gateway_server.send_notification(token, payload)
    print(' * [Info] iOS notification sent')


#############
# UTILITIES #
#############


class Config:
    """Configuration class.

    Makes reading and writing from config slightly easier. Simple treat the
    config object using a with statement.

    with Config() as config:
        config['key'] = 'some value'
    """

    def __init__(self,
            fs_dir: str='./',
            path: str='config.json',
            default_log_dir: str='logs',
            default_port: int=5678):
        """
        Note that the default kwargs will not take effect if the associated
        keys already exist in the config file."""
        self.path = os.path.join(fs_dir, path)
        self.defaults = {
            'log_dir': os.path.join(fs_dir, default_log_dir),
            'port': default_port,
            'token': ''
        }
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump(self.defaults, f)

    def __enter__(self):
        """Read the configuration file.

        Populate the configuration with default values if necessary.
        Additionally ensure that the log directory exists.
        """
        with open(self.path, 'r') as f:
            self.data = json.load(f)
        for key, value in self.defaults.items():
            self.data[key] = self.data.get(key, value)
        os.makedirs(self.data['log_dir'], exist_ok=True)
        return self.data

    def __exit__(self, *args):
        with open(self.path, 'w') as f:
            json.dump(self.data, f)


class VideoWritingManager:
    """Handles writing a video for periods of detected motion.

    Additionally ensures that reasonably close periods of motion are lumped
    together into a single video.
    """


    def __init__(self,
            fs_dir: str='./',
            encoding: str='MP4V',
            fps: int=5,
            max_pause_duration: int=5,
            exe_path: str='./MotioSecure-darwin-x64/MotioSecure.app/Contents/MaxOS/MotioSecure'):
        self.fs_dir = fs_dir
        self.exe_path = exe_path
        self.false_start = time.time()
        self.encoding = encoding
        self.fps = fps
        self.max_pause_duration = max_pause_duration
        self.previous_motion_detected = False
        self.writer = None

    def on_process_image(self, image: np.array, motion_detected: bool):
        """Hook for every new image processed.

        Determines whether or not to start a new video.
        """
        now = time.time()
        if not self.previous_motion_detected and motion_detected:
            long_enough = now - self.false_start > self.max_pause_duration
            if (self.writer and long_enough) or not self.writer:
                self.start_new_writer(image)
                self.false_start = now
            if self.writer:
                self.writer.write(image)
        self.previous_motion_detected = motion_detected

    def start_new_writer(self, image: np.array):
        """Start a new video path at some path, selected as function of time."""
        print(' * [Info] Start new video writer.')
        with Config(self.fs_dir) as config:
            if config.get('token', None):
                send_ios_notification(
                    config['token'], self.fs_dir, self.exe_path)
            video_path = os.path.join(
                self.fs_dir, config['log_dir'], 'video%s.mp4' % time.time())
        width, height, _ = image.shape
        self.writer = cv2.VideoWriter(
            video_path,
            cv2.VideoWriter_fourcc(*self.encoding),
            self.fps,
            (height, width))


if __name__ == '__main__':
    try:
        main()
    except:
        e = sys.exc_info()[0]
        with open(os.path.join(fs_dir, 'log_python.txt'), 'a') as f:
            f.write(str(e))
