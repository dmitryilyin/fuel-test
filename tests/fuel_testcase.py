#    Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import logging
from unittest import TestCase

from devops.helpers.helpers import SSHClient, wait
from environment.fuel_environment import FuelEnvironment
from helpers.cobbler_client import CobblerClient
from helpers.config_astute import AstuteConfig
from helpers.functions import write_config
from helpers.decorators import debug
from helpers.nailgun_client import NailgunClient

from settings import DOMAIN_NAME_WDOT


logger = logging.getLogger(__name__)
logwrap = debug(logger)


class FuelTestCase(TestCase):
    def setUp(self):
        self.env = FuelEnvironment()
        self.env.get_empty_state()
        self.client = NailgunClient(self.env.get_master_ip())

    def get_master_ssh(self):
        """
        :rtype : SSHClient
        """
        return self.env.get_master_ssh()

    def get_master_ip(self):
        return self.env.get_master_ip()


    @logwrap
    def generate_astute_config(self):
        config = AstuteConfig(self.env).generate()
        config_path = "/root/astute.yaml"
        write_config(self.get_master_ssh(), config_path, str(config))

    @logwrap
    def get_node_by_devops_node(self, devops_node):
        """Returns dict with nailgun slave node description if node is
        registered. Otherwise return None.
        """
        mac_addresses = map(
            lambda interface: interface.mac_address.capitalize(),
            devops_node.interfaces)
        for nailgun_node in self.client.list_nodes():
            if nailgun_node['mac'].capitalize() in mac_addresses:
                nailgun_node['devops_name'] = devops_node.name
                return nailgun_node
        return None

    def nailgun_nodes(self, devops_nodes):
        return map(lambda node: self.get_node_by_devops_node(node), devops_nodes)

    def devops_nodes_by_names(self, devops_node_names):
        return map(lambda name: self.env.get_env().node_by_name(name), devops_node_names)

    @logwrap
    def cobbler_configure(self):
        master = self.env.nodes().admin
        client = CobblerClient(master.get_ip_address_by_network_name('internal'))
        token = client.login('cobbler', 'cobbler')
        for node in self.env.nodes().slaves:
            self.add_node(client,
                          token,
                          master,
                          node,
                          gateway=master.get_ip_address_by_network_name('internal'),
                          net_mask=self.env.internal_net_mask()
            )

    def add_node(self, client, token, cobbler, node, gateway, net_mask):
        node_name = node.name
        node_mac0 = str(node.interfaces[0].mac_address)
        node_mac1 = str(node.interfaces[1].mac_address)
        node_mac2 = str(node.interfaces[2].mac_address)
        node_ip = str(node.get_ip_address_by_network_name('internal'))
        self._add_node(client,
                       token,
                       cobbler,
                       node_name,
                       node_mac0,
                       node_mac1,
                       node_mac2,
                       node_ip,
                       gateway=gateway,
                       net_mask=net_mask,
            )

    def _add_node(self, client, token, cobbler, node_name, node_mac0, node_mac1,
                  node_mac2, node_ip, gateway, net_mask):
        system_id = client.new_system(token)
        profile = "bootstrap"
        client.modify_system_args(system_id,
                                  token,
                                  name=node_name,
                                  hostname=node_name,
                                  name_servers=cobbler.get_ip_address_by_network_name('internal'),
                                  name_servers_search="localdomain",
                                  profile=profile,
                                  gateway=gateway,
                                  netboot_enabled="1")
        client.modify_system(system_id, 'modify_interface', {
            "macaddress-eth0": str(node_mac0),
            "ipaddress-eth0": str(node_ip),
            "netmask-eth0": str(net_mask),
            "dnsname-eth0": node_name + DOMAIN_NAME_WDOT,
            "static-eth0": "1",
            "macaddress-eth1": str(node_mac1),
            "static-eth1": "1",
            "macaddress-eth2": str(node_mac2),
            "static-eth2": "1"
        }, token)
        client.save_system(system_id, token)
        client.sync(token)

    @logwrap
    def bootstrap_nodes(self, timeout=600):
        """Start vms and wait they are registered on nailgun.
        :rtype : List of registred nailgun nodes
        """
        devops_nodes = self.devops_nodes_by_names([node.name for node in self.env.nodes().slaves])
        for node in devops_nodes:
            node.start()
        wait(lambda: all(self.nailgun_nodes(devops_nodes)), 15, timeout)
        return self.nailgun_nodes(devops_nodes)