#!/usr/bin/env python

import logging
import subprocess
import tarfile
from time import sleep
from devops.helpers.helpers import _wait
import os
import re
from cobbler_client import CobblerClient
from settings import OS_FAMILY

here = lambda *x: os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), *x)

root = lambda *x: os.path.join(os.path.abspath(here('..')), *x)


def write_config(remote, path, text):
    config = remote.open(path, 'w')
    config.write(text)
    logging.info('Write config %s' % text)
    config.close()


def install_packages(remote, packages):
    if OS_FAMILY == "centos":
        remote.sudo.ssh.check_call('yum -y install %s' % packages)
    else:
        remote.sudo.ssh.check_call(
            'DEBIAN_FRONTEND=noninteractive apt-get -y install %s' % packages)


def switch_off_ip_tables(remote):
    remote.sudo.ssh.execute('iptables -F')


def upload_recipes(remote, local_dir=None, remote_dir="/etc/puppet/modules/"):
    """
    Upload puppet modules.
    """
    recipes_dir = local_dir or root('deployment', 'puppet')
    tar_file = None
    try:
        tar_file = remote.open('/tmp/recipes.tar', 'wb')

        with tarfile.open(fileobj=tar_file, mode='w', dereference=True) as tar:
            tar.add(recipes_dir, arcname='')

        remote.mkdir(remote_dir)
        remote.check_call('tar xmf /tmp/recipes.tar --overwrite -C %s' % remote_dir)
    finally:
        if tar_file:
            tar_file.close()


def upload_keys(remote, remote_dir="/var/lib/puppet/"):
    ssh_keys_dir = root('fuel-test', 'config', 'ssh_keys')
    remote.upload(ssh_keys_dir, remote_dir)