from subprocess import call

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


class MotioSecureApi:

    num_monitor_threads = 0
    should_stop_thread = False

    def accept(self, contact: str):
        """Add contact information to auto-accept whitelist.

        :param contact: Phone number preceded by country code or email address
                        associated with an iCloud account. Leave empty to get
                        first contact.
        """
        with Config() as config:
            if not contact:
                return config.get('accept', [''])[0]
            if 'accept' not in config:
                config['accept'] = []
            config['accept'].append(contact)
        call('defaults write com.apple.FaceTime AutoAcceptInvitesFrom -array-add'.split(' ') + [contact])
        return 'Successfully added contact'

    def token(self, token: str):
        """Add new mobile device token to configuration.

        :param token: String hex code taken from the iOS application. Leave
                      empty to get token.
        """
        with Config() as config:
            if not token:
                return config['token']
            config['token'] = token
        return 'Successfully added token'

    def echo(self, text: str) -> str:
        return text


def main():
    s = zerorpc.Server(MotioSecureApi())
    s.bind('tcp://127.0.0.1:4242')
    print('start running on 4242')
    s.run()


# The following was taken from the `web/` interface. This code should mirror
# those files accordingly.


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
            path: str='config.json',
            default_log_dir: str='logs',
            default_port: int=5678):
        """
        Note that the default kwargs will not take effect if the associated
        keys already exist in the config file."""
        self.path = path
        self.defaults = {
            'log_dir': default_log_dir,
            'port': default_port
        }
        if not os.path.exists(path):
            with open(path, 'w') as f:
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


if __name__ == '__main__':
    main()
