"""Utilities for processing tasks on beardo's build queue
"""
# future imports
from __future__ import absolute_import
from __future__ import unicode_literals

# stdlib imports
import json
import subprocess
import tempfile

# third-party imports
import requests

# local imports
from .logger import logger


class NoopTask(object):

    def run(self):
        logger('No tasks in queue: Nothing to report.', level='DEBUG')


def run_process(cmd_args, cwd=None):
    """Runs the given process and returns its output and exit code.
    """
    try:
        return subprocess.check_output(cmd_args, stderr=subprocess.STDOUT, cwd=cwd), 0
    except subprocess.CalledProcessError, e:
        return e.output, e.returncode


class Task(object):

    def __init__(self, task_data, queue):
        self.task_data = task_data
        self.queue = queue

    def get_commands(self):
        """Generates commands that get passed to subprocess and run the actual build.
        """
        # check out the relevant commit into a temporary directory
        tmpdir = tempfile.mkdtemp()
        yield ['git', 'clone', self.task_data['payload']['repository']['url'], tmpdir], None
        # check out the branch that was just pushed
        yield ['git', 'checkout', self.task_data['payload']['ref']], tmpdir
        # hard reset to the given commit in case another has been pushed since this build was generated
        yield ['git', 'reset', '--hard', self.task_data['payload']['after']], tmpdir
        # run docker build on the checked out code
        container_name = self.queue.registry_url + '/' + self.task_data['task_name']
        yield ['docker', 'build', '-t', container_name, '.'], tmpdir
        # push the container to the private registry
        yield ['docker', 'push', container_name], tmpdir

    def run(self):
        """Runs the leased task and records the output (stdout and stderr).
        """
        # run the build and store the output
        logger('Processing task: {0}'.format(self.task_data['task_name']))
        results = []
        for command, cwd in self.get_commands():
            _output, _retcode = run_process(command, cwd=cwd)
            results.append({
                'command': ' '.join(command),
                'output': _output.splitlines(),
                'returncode': _retcode,
            })
            if bool(_retcode):
                break

        # store task output and success/failure status alongside the other
        # task data (it's useful when sending data back to the server so we
        # can store build logs, use the original task name, etc.)
        self.task_data['success'] = not bool(sum(x['returncode'] for x in results))
        self.task_data['build_logs'] = results

        # log build output and report results to control server
        self.record_build()

    def record_build(self):
        """Log build output and report result via HTTP request to the control server.
        """
        # log build output
        for command in self.task_data['build_logs']:
            logger('**{0}'.format(command['command']))
            for log_line in command['output']:
                logger(log_line, level="DEBUG")
        if self.task_data['success']:
            logger('Task completed successfully.')
        else:
            logger('There was an error with the task, please inspect the logs.', level="ERROR")

        # posts all task data to the control server, authorising the requests
        # as necessary
        response = requests.post(
            self.queue.complete_url,
            auth=(self.queue.auth_username, self.queue.auth_password),
            data=json.dumps(self.task_data),
        )

        # uses response code from the HTTP request to indicate status.
        if response and response.status_code == 200:
            logger('Task marked complete: {0}'.format(self.task_data['task_name']))
            return True
        logger('Unable to complete task: {0}'.format(self.task_data['task_name']), level="ERROR")
        return False
