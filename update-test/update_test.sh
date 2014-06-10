#!/bin/sh

ENV_ID="${1}"
NODE_ID="${2}"
VERSION="${3}"
OS="${4}"

if [ "${ENV_ID}" == "" ]; then
  ENV_ID="1"
fi

if [ "${NODE_ID}" == "" ]; then
  NODE_ID="1"
fi

if [ "${VERSION}" == "" ]; then
  VERSION="5.1"
fi

if [ "${OS}" == "" ]; then
  OS="centos"
fi

### functions ###

# basic #

upload_from_stdin() {
  dockerctl shell "${1}" "tee ${2}" > /dev/null
}

set_env_error() {
cat <<EOF | upload_from_stdin nailgun set_env_error.sh
  python -c "
from nailgun.db import db
from nailgun.objects import Cluster
cluster = Cluster.get_by_uid(${ENV_ID})
if not cluster:
    print 'No cluster: ' + '${ENV_ID}'
    exit(1)
Cluster.update(cluster, {'status': 'error'})
db().commit()
"
  if [ \$? -gt 0 ]; then
    echo "Could not set env status to error!"
    exit 1
  fi
EOF
  dockerctl shell nailgun "sh set_env_error.sh"
}

set_node_error() {
cat <<EOF | upload_from_stdin nailgun set_node_error.sh
  python -c "
from nailgun.db import db
from nailgun.db.sqlalchemy.models import Node
node_db = db().query(Node).get(${NODE_ID})
if not node_db:
    print 'No node: ' + '${NODE_ID}'
    exit(1)
setattr(node_db, 'status', 'error')
db().add(node_db)
db().commit()
"
  if [ \$? -gt 0 ]; then
    echo "Could not set node status to error!"
    exit 1
  fi
EOF
  dockerctl shell nailgun "sh set_node_error.sh"
}

fuel_deploy_changes() {
  fuel --env "${ENV_ID}" deploy-changes
  if [ $? -gt 0 ]; then
    echo "Deploy run have failed!"
    exit 1
  fi
}

fuel_download_deployment_config() {
  fuel --env "${ENV_ID}" deployment default
  if [ $? -gt 0 ]; then
    fuel --env "${ENV_ID}" deployment download
  fi

  YAML=$(ls deployment_${ENV_ID}/*_${NODE_ID}.yaml | head -n 1)
  if ! [ -f "${YAML}" ]; then
    echo "Could not download node's config!"
    exit 1
  fi
}

fuel_upload_deployment_config() {
  fuel --env "${ENV_ID}" deployment upload
  if [ $? -gt 0 ]; then
    echo "Could not upload node's config!"
    exit 1
  fi
  rm -rf "deployment_${ENV_ID}"
}

# advanced #

set_yaml_data() {
  version="${1}"
  fuel_download_deployment_config
  ruby -e "
  require 'yaml'
  yaml = YAML.load_file '${YAML}'
  unless yaml
    puts 'Could not load env settings form ${YAML}'
    exit 1
  end
  version_data_centos = {
    '5.0' => {
      'repo_metadata' => {
        'nailgun' => 'http://10.20.0.2:8080/centos/fuelweb/x86_64/',
      },
      'puppet_modules_source'   => 'rsync://10.20.0.2/puppet/releases/5.0/modules/',
      'puppet_manifests_source' => 'rsync://10.20.0.2/puppet/releases/5.0/manifests/',
    },
    '5.1' => {
      'repo_metadata' => {
        'nailgun' => 'http://10.20.0.2:8080/centos/fuelweb/x86_64/',
        'update'  => 'http://10.20.0.2:8080/centos-fuel-5.1-update/centos/',
      },
      'puppet_modules_source'   => 'rsync://10.20.0.2/puppet/releases/5.1/modules/',
      'puppet_manifests_source' => 'rsync://10.20.0.2/puppet/releases/5.1/manifests/',
    },
  }
  version_data_ubuntu = {
    '5.0' => {
      'repo_metadata' => {
        'nailgun' => 'http://10.20.0.2:8080/ubuntu/fuelweb/x86_64 precise main',
      },
      'puppet_modules_source'   => 'rsync://10.20.0.2/puppet/releases/5.0/modules/',
      'puppet_manifests_source' => 'rsync://10.20.0.2/puppet/releases/5.0/manifests/',
    },
    '5.1' => {
      'repo_metadata' => {
        'nailgun' => 'http://10.20.0.2:8080/ubuntu/fuelweb/x86_64 precise main',
        'update'  => 'http://10.20.0.2:8080/ubuntu-fuel-5.1-update/reprepro/ precise main',
      },
      'puppet_modules_source'   => 'rsync://10.20.0.2/puppet/releases/5.1/modules/',
      'puppet_manifests_source' => 'rsync://10.20.0.2/puppet/releases/5.1/manifests/',
    },
  }

  version_data = version_data_${OS}

  unless version_data.key? '${version}'
    puts 'No such version in data structure ${version}'
    exit 1
  end
  yaml = yaml.merge version_data['${version}']
  File.open('${YAML}', 'w') { |file| file.write YAML.dump yaml }
"
  if [ $? -gt 0 ]; then
    echo "Could not set yaml data to version ${version}"
    exit 1
  fi
  fuel_upload_deployment_config
}

update() {
  set_env_error && set_node_error
  set_yaml_data "${1}"
  if [ "${OS}" = "ubuntu" ]; then
    add_repo_key
  fi
  fuel_deploy_changes
  get_pkg_version
}

get_node_ip() {
  fuel nodes | ruby -n -e "
    line = \$_.split('|').map { |f| f.chomp.strip }
    puts line[4] if line[0] == '${NODE_ID}' and line[3] == '${ENV_ID}'
  "
}

add_repo_key() {
  ip=$(get_node_ip)
  cat "mirantis.key" | ssh "${ip}" "apt-key add -"
}

get_pkg_version() {
  ip=$(get_node_ip)
  if [ "${ip}" = "" ]; then
    exit 1
  fi

  if [ "${OS}" = "centos" ]; then
    ssh "${ip}" "rpm -qa openstack-glance"
  elif [ "${OS}" = "ubuntu" ]; then
    ssh "${ip}" "dpkg -l glance-api"  | grep "^ii"
  else
    exit 1
  fi

}

### MAIN ###

update "${VERSION}"
