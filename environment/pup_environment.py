#!/usr/bin/env python
import os
from devops.helpers.helpers import tcp_ping, wait
from helpers.functions import upload_recipes
from environment.environment import Environment
from settings import BASE_IMAGE


class PuppetEnvironment(Environment):
    """
    Class for create environment in puppet modules testing.
    """
    def __init__(self, base_image=None):
        """
        Constructor for create environment.
        """
        self.name = os.environ.get('ENV_NAME', 'pup-integration')
        self.base_image = base_image or BASE_IMAGE
        super(PuppetEnvironment, self).__init__(self.name, self.base_image)
        self.environment = super(PuppetEnvironment, self).get_env()
        self.start_all()

    def snapshot_exist(self, snap_name="before_test"):
        return self.environment.has_snapshot(name=snap_name)

    def snapshot_create(self, snap_name="", description="", force=True):
        """
        Create snapshot for environment.
        """
        self.environment.snapshot(name=snap_name, description=description, force=force)

    def snapshot_revert(self, snap_name="", destroy=True):
        """
        Revert environment to snapshot by name.
        """
        self.environment.revert(name=snap_name, destroy=destroy)

    def execute_cmd(self, command, debug=True):
        """
        Execute command on node.
        """
        return self.get_master_ssh().execute(command, verbose=debug)['exit_code']

    def upload_files(self, source, dest):
        """
        Upload file(s) to node.
        """
        self.get_master_ip().upload(source, dest)

    def upload_modules(self, local_dir, remote_dir="/etc/puppet/modules/"):
        """
        Upload puppet modules.
        """
        upload_recipes(remote=self.get_master_ssh(), local_dir=local_dir, remote_dir=remote_dir)

    def await(self, timeout=1200):
        wait(
            lambda: tcp_ping(self.get_master_ip(), 22), timeout=timeout)


if __name__ == "__main__":
    env = PuppetEnvironment(base_image='/var/lib/libvirt/images/centos6.4-base.qcow2')
    env.await()
    env.upload_modules('/home/alan/fuel/deployment/puppet')
    env.snapshot_create(snap_name="test1")
    env.execute_cmd('apt-get install mc')
    env.erase()



