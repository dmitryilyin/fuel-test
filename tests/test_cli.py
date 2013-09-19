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
import unittest
from helpers.decorators import snapshot_errors, debug, fetch_logs
from settings import USE_SNAP
from tests.fuel_testcase import FuelTestCase

logging.basicConfig(
    format=':%(lineno)d: %(asctime)s %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)
logwrap = debug(logger)


class TestCLI(FuelTestCase):
    @snapshot_errors
    @logwrap
    @fetch_logs
    def test_nodes_provision(self):
        if USE_SNAP and self.env.get_env().has_snapshot(name="provisioned"):
            self.env.get_env().revert(name="provisioned")
        else:
            self.cobbler_configure()
            self.bootstrap_nodes()
            self.generate_astute_config()
            ps_out = self.get_master_ssh().execute('ls -al /root/')['stdout']
            logging.debug('!!! Output of /root: %s' % ps_out)
            res = self.get_master_ssh().execute("astute -f /root/astute.yaml -c provision", True)['exit_code']
            self.assertEqual(0, res)
            self.env.get_env().snapshot(name="provisioned", force=True)

        res = self.get_master_ssh().execute("astute -f /root/astute.yaml -c deploy", True)['exit_code']
        logging.debug('!!! Deploy result: %s' % res)
        self.assertEqual(0, res)
        err = self.get_master_ssh().execute("find /var/log/remote -name puppet-agent.log -print0 | xargs -0 -I @ grep 'err:' '@' | wc -l", True)['stdout'][0]
        self.env.get_env().snapshot(name="deployed", force=True)
        logging.debug('!!! Count of errors in puppet-agent logs: %s' % err)
        self.assertEqual(0, int(err))


if __name__ == '__main__':
    unittest.main()
