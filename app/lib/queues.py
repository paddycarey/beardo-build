"""Utilities for interacting with beardo's build queue
"""
# future imports
from __future__ import absolute_import
from __future__ import unicode_literals

# third-party imports
import requests

# local imports
from .logger import logger
from .tasks import NoopTask
from .tasks import Task


class Queue(object):

    def __init__(self, config):
        self.lease_url = config['QUEUE_URL_LEASE']
        self.complete_url = config['QUEUE_URL_COMPLETE']
        self.registry_url = config['REGISTRY_URL']
        self.auth_username = config['QUEUE_USERNAME']
        self.auth_password = config['QUEUE_PASSWORD']

    def lease(self):
        """Fetches the next job from the queue and returns a fully fledged
        task instance.
        """
        logger('Requesting build task from queue.', level='DEBUG')
        response = requests.get(
            self.lease_url,
            auth=(self.auth_username, self.auth_password),
        )

        if response and response.status_code == 200:
            return Task(response.json(), self)

        return NoopTask()
