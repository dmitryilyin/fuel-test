import yaml
from environment.environment import Environment
from settings import DOMAIN_NAME_WDOT, DEPLOYMENT_MODE, DEPLOY_SIMPLE


class AstuteConfig():
    def __init__(self, env, deployment_mode=None):
        self.env = env
        self.master_ip = self.env.get_master_ip()
        self.deploy = DEPLOYMENT_MODE or deployment_mode

    def generate(self, **kwargs):
        config = {
            "attributes": self.attributes(**kwargs),
            "engine": self.engine(**kwargs),
            "nodes": self.nodes(**kwargs),
            "common_ks_meta": self.common_ks_meta(**kwargs),
            "common_power_info": self.power_info(**kwargs),
            "common_node_settings": self.common_node_settings(**kwargs),
        }

        config.update(self.task_uuid())

        return yaml.safe_dump(config, default_flow_style=False)

    def nodes(self, **kwargs):
        nodes = []
        for node in self.env.nodes().slaves:
            node_info = {
                            "name": node.name,
                            "hostname": node.name + DOMAIN_NAME_WDOT,
                            "profile": kwargs.get('profile', 'centos-x86_64'),
                            "ks_meta": self._get_ks_meta(node),
                            "interfaces": self._get_interfaces(node),
                            "public_br": 'br-ex',
                            "internal_br": 'br-mgmt',
                            "roles": [self._get_role(node.name)],
                            "default_gateway": self.env.get_router_by_netname('internal'),
                            #"fqdn": node.name + DOMAIN_NAME_WDOT,
                            #"error_type": "",
                            "network_data": self._get_network_data(node),

            }

            nodes.append(node_info)

        return nodes

    def _get_role(self, node_name):
        if "controller" in node_name:
            return self._get_controller_role(node_name)
        elif "compute" in node_name:
            return "compute"
        elif "swift-proxy" in node_name:
            return self._get_proxy_role(node_name)
        elif "swift" in node_name:
            return "storage"

        return None

    def _get_controller_role(self, node_name):
        return "primary-controller" if self.deploy is not DEPLOY_SIMPLE and "controller-01" in node_name else "controller"

    def _get_proxy_role(self, node_name):
        return "primary-swift-proxy" if "swift-proxy-01" in node_name else "swift-proxy"

    def _get_network_data(self, node):
        public_net = {"name": "public",
                      "ip": node.get_ip_address_by_network_name('public'),
                      "dev": "eth1",
                      "netmask": "255.255.255.0",
                      }
        management_net = {"name": ["management", "storage"],
                        "ip": node.get_ip_address_by_network_name('internal'),
                        "dev": "eth0",
                        "netmask": "255.255.255.0",
                      }

        fixed_net = {"name": "fixed",
                        #"ip": node.get_ip_address_by_network_name('private'),
                        "dev": "eth2",
                        #"netmask": "255.255.255.0",
                      }

        nets = [public_net, management_net, fixed_net]

        return nets

    def _get_ks_meta(self, node):
        size = int(self.env.get_volume_capacity(node) / (1024 * 1024))
        pv_size = (size - 564)
        ks_meta = {'ks_disks': [
                                {'type': "disk",
                                 "id": "vda",
                                 "size": size,
                                 "volumes":[{"type": "boot", "size": 300},
                                            {"type": "partition", "size": 200, "mount": "/boot"},
                                            {"type": "lvm_meta", "size": 64, "name": "os"},
                                            {"type": "pv", "size": pv_size, "vg": "os"}
                                 ]},
                                {'type': "vg", #//TODO: vg decrease 64 => (pv_size-1024) - 64
                                 "id": "os",
                                 "min_size": pv_size,
                                 "label": "Base System",
                                 "volumes":[{"type": "lv", "mount": "/", "name": "root", "size": (pv_size - 1024) - 64},
                                            {"type": "lv", "mount": "/swap", "name": "swap", "size": 1024},

                                 ]}
        ]}

        return ks_meta

    def _get_interfaces(self, node):
        return [
            {
                "name": "eth0",
                "ip_address": node.get_ip_address_by_network_name('internal'),
                "dns_name": node.name + DOMAIN_NAME_WDOT,
                "static": 0,
                "mac_address": node.interfaces.filter(network__name='internal')[0].mac_address,
                "onboot": 'yes',
                "peerdns": 'no',
                "use_for_provision": True
            },
            {
                "name": "eth1",
                "ip_address": node.get_ip_address_by_network_name('public'),
                "mac_address": node.interfaces.filter(network__name='public')[0].mac_address,
                "static": 0,
                "onboot": 'no',
                "peerdns": 'no',
            },
            {
                "name": "eth2",
                "ip_address": node.get_ip_address_by_network_name('private'),
                "mac_address": node.interfaces.filter(network__name='private')[0].mac_address,
                "static": 0,
                "onboot": 'no',
                "peerdns": 'no',
            }
        ]

    def attributes(self, **kwargs):
        quantum = kwargs.get('quantum', True)

        fixed_network_range = '.'.join(self.env.get_master_ip().split('.')[:-1] + ['0/24'])
        floating_network_range = '.'.join(self.env.get_master_ip('public').split('.')[:-1] + ['150/26']) if quantum else \
                                    [kwargs.get('floating_network_range', self.master_ip)]

        attr = {'use_cow_images': kwargs.get('use_cow_images', True),
                'libvirt_type': kwargs.get('libvirt_type', 'qemu'),
                'dns_nameservers': [kwargs.get('master_ip', self.master_ip)],
                #'verbose': kwargs.get('verbose', True),
                #'debug': kwargs.get('verbose', True),
                'auto_assign_floating_ip': kwargs.get('auto_assign_floating_ip', True),
                'start_guests_on_host_boot': kwargs.get('start_guests_on_host_boot', True),
                'create_networks': kwargs.get('create_networks', True),
                'compute_scheduler_driver': kwargs.get('compute_scheduler_driver', 'nova.scheduler.multi.MultiScheduler'),
                'quantum': quantum,
                'master_hostname': kwargs.get('master_hostname', 'master' + DOMAIN_NAME_WDOT),
                'master_ip': kwargs.get('master_ip', self.master_ip),
                'nagios': kwargs.get('nagios', False),
                'nagios_master': kwargs.get('nagios_master', 'master' + DOMAIN_NAME_WDOT),
                'proj_name': kwargs.get('proj_name', self.env.name),
                'management_vip': kwargs.get('management_vip', self.env.internal_virtual_ip()),
                'public_vip': kwargs.get('public_vip', self.env.public_virtual_ip()),
                'quantum_parameters': {
                                        'tenant_network_type': kwargs.get('tenant_network_type', 'gre'),
                                        'segment_range': kwargs.get('segment_range', '300:500'),
                                        'metadata_proxy_shared_secret': kwargs.get('metadata_proxy_shared_secret', 'quantum'),
                                    },
                'mysql': {
                            'root_password': kwargs.get('root_password', 'root'),
                        },

                'glance': {
                            'db_password': kwargs.get('glance_db_password', 'glance'),
                            'user_password': kwargs.get('glance_user_password', 'glance'),
                        },

                'swift': {
                            'user_password': kwargs.get('swift_user_password', 'swift_pass'),
                        },

                'nova': {
                            'db_password': kwargs.get('nova_db_password', 'nova'),
                            'user_password': kwargs.get('nova_user_password', 'nova'),
                        },
                'access': {
                            'password': kwargs.get('access_password', 'admin'),
                            'user': kwargs.get('access_user', 'admin'),
                            'tenant': kwargs.get('tenant', 'admin'),
                            'email': kwargs.get('email', 'admin@example.org'),

                        },
                'keystone': {
                            'db_password': kwargs.get('keystone_db_password', 'keystone'),
                            'admin_token': kwargs.get('admin_token', 'nova'),
                        },
                'quantum_access': {
                            'user_password': kwargs.get('quantum_user_password', 'quantum'),
                            'db_password': kwargs.get('quantum_db_password', 'quantum'),
                        },
                'rabbit': {
                            'password': kwargs.get('rabbit_password', 'nova'),
                            'user': kwargs.get('rabbit_user', 'nova'),
                        },
                'cinder': {
                            'password': kwargs.get('cinder_password', 'cinder'),
                            'user': kwargs.get('cinder_user', 'cinder'),
                        },
                'base_syslog': {
                            'syslog_port': kwargs.get('base_syslog_port', '514'),
                            'syslog_server': kwargs.get('base_syslog_server', self.master_ip),
                        },
                'syslog': {
                            'syslog_port': kwargs.get('syslog_port', '514'),
                            'syslog_transport': kwargs.get('syslog_transport', 'udp'),
                            'syslog_server': kwargs.get('syslog_server', self.master_ip),
                        },
                'floating_network_range': floating_network_range,
                'fixed_network_range': fixed_network_range,
                'deployment_id': kwargs.get('deployment_id', 1),
                'deployment_mode': kwargs.get('deployment_mode', self.deploy),
                'deployment_source': kwargs.get('deployment_source', 'cli'),
                'deployment_engine': kwargs.get('deployment_engine', 'nailyfact'),
                'ntp_servers': kwargs.get('ntp_servers', ['pool.ntp.org']),
                }

        return attr

    def engine(self, **kwargs):
        engine = {
                    'url': kwargs.get('url', 'http://localhost/cobbler_api'),
                    'username': kwargs.get('username', 'cobbler'),
                    'password': kwargs.get('password', 'cobbler')
        }

        return engine

    def power_info(self, **kwargs):
        power = {
                    'power_type': kwargs.get('power_type', 'ssh'),
                    'power_user': kwargs.get('power_user', 'root'),
                    'power_pass': kwargs.get('power_pass', '/root/.ssh/bootstrap.rsa'),
                    'netboot_enabled': kwargs.get('netboot_enabled', 1),
        }

        return power

    def common_node_settings(self, **kwargs):
        return {'name_servers': kwargs.get('name_servers', self.master_ip)}

    def task_uuid(self, deployment_task='deployment_task'):
        return {'task_uuid': deployment_task}

    def common_ks_meta(self, **kwargs):
        meta = {
                    'mco_enable': kwargs.get('mco_enable', 1),
                    'mco_vhost': kwargs.get('mco_vhost', 'mcollective'),
                    'mco_pskey': kwargs.get('mco_pskey', 'unset'),
                    'mco_user': kwargs.get('mco_user', 'mcollective'),
                    'puppet_enable': kwargs.get('puppet_enable', 0),
                    'install_log_2_syslog': kwargs.get('install_log_2_syslog', 1),
                    'mco_password': kwargs.get('mco_password', 'marionette'),
                    'puppet_auto_setup': kwargs.get('puppet_auto_setup', 1),
                    'puppet_master': kwargs.get('puppet_master', 'master' + DOMAIN_NAME_WDOT),
                    'mco_auto_setup': kwargs.get('mco_auto_setup', 1),
                    'auth_key': kwargs.get('auth_key', '""'),
                    'puppet_version': kwargs.get('puppet_version', '2.7.19'),
                    'mco_connector': kwargs.get('mco_connector', 'rabbitmq'),
                    'mco_host': kwargs.get('mco_host', self.master_ip)
        }

        return meta


if __name__ == "__main__":
    e = Environment()
    config_yaml = AstuteConfig(e)
    print config_yaml.generate()