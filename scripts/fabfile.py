# stdlib imports
import os
import sys

# third-party imports
from fabric.api import env
from fabric.api import put
from fabric.api import run
from fabric.api import sudo

# local imports
from libdeploy import load_config


def with_config():
    """Load configuration from file
    """
    config = load_config()

    env.user = config['USERNAME']
    env.key_filename = '/secrets/deploy/deploy.pem'
    env.hosts = [config['HOSTNAME']]


def enable_and_start_service(service_path):

    # upload the service file
    service_name = os.path.split(service_path)[1]
    put(service_path, '/etc/systemd/system/{0}'.format(service_name), use_sudo=True)

    # enable and (re)start the service
    sudo('systemctl enable {0}'.format('/etc/systemd/system/{0}'.format(service_name)))
    sudo('systemctl restart {0}'.format(service_name))


def upload_container():
    run('mkdir -p /home/core/bw1/')
    put('/build/beardo-build.tar.gz', '/home/core/bw1/beardo-build.tar.gz')
    run('gunzip -f /home/core/bw1/beardo-build.tar.gz')
    sudo('docker load < /home/core/bw1/beardo-build.tar')
    sudo('docker images')


def upload_deploy_configuration():
    put('/secrets/gitlab/deploy-key.pem', '/home/core/bw1/deploy-key.pem')
    put('/secrets/gitlab/deploy_known_hosts', '/home/core/bw1/deploy_known_hosts')
    put('/secrets/conf/deploy.conf', '/home/core/bw1/deploy.conf')


def service_status():
    sudo('systemctl status build.service')


def deploy():
    """Deploy current working tree to server
    """

    # upload container to server
    upload_container()
    # upload deploy configuration to server
    upload_deploy_configuration()
    # deploy a private registry
    enable_and_start_service('/assets/build.service')
    service_status()
