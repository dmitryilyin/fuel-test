import os

#[main]
DEPLOY_SIMPLE = "multinode"
DEPLOY_COMPACT = "ha"
DEPLOY_FULL = "ha_full"

OS_FAMILY = os.environ.get('OS_FAMILY', "centos")

ISO_PATH = os.environ.get('ISO_PATH', '/home/Downloads/fuellib_test.iso')

DEPLOYMENT_MODE = os.environ.get('DEPLOYMENT_MODE', DEPLOY_SIMPLE)

DEFAULT_IMAGES = {
    'centos': '/var/lib/libvirt/images/centos6.4-base.qcow2',
    'ubuntu': '/var/lib/libvirt/images/ubuntu-12.04.1-server-amd64-p2.qcow2',
}

BASE_IMAGE = os.environ.get('BASE_IMAGE', DEFAULT_IMAGES.get(OS_FAMILY))

PROFILES_COBBLER_COMMON = {
    'centos': 'centos64_x86_64',
    'ubuntu': 'ubuntu_1204_x86_64'
}

CURRENT_PROFILE = PROFILES_COBBLER_COMMON.get(OS_FAMILY)

DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'localdomain')
DOMAIN_NAME_WDOT = '.' + DOMAIN_NAME

EMPTY_SNAPSHOT = os.environ.get('EMPTY_SNAPSHOT', 'empty')

LOGS_DIR = os.environ.get('LOGS_DIR', '/home/alan/test-logs')

USE_SNAP = os.environ.get('USE_SNAP', True)

#[tempest]
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'nova'
ADMIN_TENANT_ESSEX = 'openstack'
ADMIN_TENANT_FOLSOM = 'admin'

CIRROS_IMAGE = os.environ.get('CIRROS_IMAGE', 'http://srv08-srt.srt.mirantis.net/cirros-0.3.0-x86_64-disk.img')

#[nodes]
DEFAULT_RAM_SIZE = int(os.environ.get('DEFAULT_RAM_SIZE', 2048))
COMPUTE_RAM_SIZE = int(os.environ.get('COMPUTE_RAM_SIZE', 2048))

COUNT_NODES = {
    DEPLOY_SIMPLE: {
        "CONTROLLERS": int(os.environ.get('CONTROLLERS', 1)),
        "COMPUTES": int(os.environ.get('COMPUTES', 3)),
        "STORAGES": int(os.environ.get('STORAGES', 0)),
        "PROXIES": int(os.environ.get('PROXIES', 0)),
        "QUANTUMS": int(os.environ.get('QUANTUMS', 0))
    },

    DEPLOY_COMPACT: {
        "CONTROLLERS": int(os.environ.get('CONTROLLERS', 3)),
        "COMPUTES": int(os.environ.get('COMPUTES', 3)),
        "STORAGES": int(os.environ.get('STORAGES', 0)),
        "PROXIES": int(os.environ.get('PROXIES', 0)),
        "QUANTUMS": int(os.environ.get('QUANTUMS', 0))
    },

    DEPLOY_FULL: {
        "CONTROLLERS": int(os.environ.get('CONTROLLERS', 3)),
        "COMPUTES": int(os.environ.get('COMPUTES', 3)),
        "STORAGES": int(os.environ.get('STORAGES', 3)),
        "PROXIES": int(os.environ.get('PROXIES', 2)),
        "QUANTUMS": int(os.environ.get('QUANTUMS', 0))
    },

    'puppet_integration': {
        "CONTROLLERS": int(os.environ.get('CONTROLLERS', 0)),
        "COMPUTES": int(os.environ.get('COMPUTES', 0)),
        "STORAGES": int(os.environ.get('STORAGES', 0)),
        "PROXIES": int(os.environ.get('PROXIES', 0)),
        "QUANTUMS": int(os.environ.get('QUANTUMS', 0))
    },
    'test_env': {
        "CONTROLLERS": int(os.environ.get('CONTROLLERS', 0)),
        "COMPUTES": int(os.environ.get('COMPUTES', 0)),
        "STORAGES": int(os.environ.get('STORAGES', 0)),
        "PROXIES": int(os.environ.get('PROXIES', 0)),
        "QUANTUMS": int(os.environ.get('QUANTUMS', 0))
    },

    }

#[network]
NET_PUBLIC = 'public'
NET_INTERNAL = 'internal'
NET_PRIVATE = 'private'

INTERFACE_ORDER = (
    NET_INTERNAL,
    NET_PUBLIC,
    NET_PRIVATE
)

FORWARDING = {
    NET_INTERNAL: os.environ.get('PUBLIC_FORWARD', 'nat'),
    NET_PUBLIC: None,
    NET_PRIVATE: None,
}

DHCP = {
    NET_PUBLIC: False,
    NET_INTERNAL: False,
    NET_PRIVATE: False,
}

DEFAULT_POOLS = {
    'centos': {
        'public': '10.108.0.0/16:24',
        'private': '10.108.0.0/16:24',
        'internal': '10.108.0.0/16:24',
        },
    'ubuntu': {
        'public': '10.107.0.0/16:24',
        'private': '10.107.0.0/16:24',
        'internal': '10.107.0.0/16:24',
        },
}

POOLS = {
    NET_PUBLIC: os.environ.get('PUBLIC_POOL', DEFAULT_POOLS.get(OS_FAMILY).get('public')).split(':'),
    NET_PRIVATE: os.environ.get('PRIVATE_POOL', DEFAULT_POOLS.get(OS_FAMILY).get('private')).split(':'),
    NET_INTERNAL: os.environ.get('INTERNAL_POOL', DEFAULT_POOLS.get(OS_FAMILY).get('internal')).split(':')
}

NETWORK_MANAGERS = {
    "flat": 'FlatDHCPManager',
    'vlan': 'VlanManager'
}