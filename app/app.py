#!/usr/bin/env python
"""Worker process that pulls docker build jobs from a queue and runs them.
"""
# future imports
from __future__ import absolute_import
from __future__ import unicode_literals

# third-party imports
from sheep import Shepherd

# local imports
from lib.config import load_config
from lib.queues import Queue


class BuildWorker(Shepherd):
    """Console worker used to process build jobs from an appengine queue.
    """

    def get_description(self):
        """Pretty worker name, purely for logging purposes.
        """
        return "BuildWorker"

    def do_work(self):
        """Main body of the task, run over and over again continuously
        """

        conf = load_config('/app.conf')
        # get the next job from the configured queue
        queue = Queue(conf)
        task = queue.lease()

        # process the job, building a container if required
        task.run()


if __name__ == "__main__":

    # run our worker process
    BuildWorker.run()
