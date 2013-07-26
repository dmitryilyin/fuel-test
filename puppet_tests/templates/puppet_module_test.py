import logging
import unittest
from helpers.env_manager import EnvManager

LOG = logging.getLogger(__name__)


class TestPuppetModule{{ module.name|title }}(unittest.TestCase):
    def setUp(self):
        self.env = EnvManager()
        self.env.await()
        self.puppet_apply = "puppet apply --verbose --detailed-exitcodes --modulepath='{{ internal_modules_path }}'"

        if not self.env.snapshot_exist(snap_name="before_test"):
            self.env.create_snapshot_env(snap_name="before_test")

        self.env.upload_modules('{{ modules_path }}', '{{ internal_modules_path }}')

{% for test in module.tests %}
    def test_{{ test.name|title }}(self):
        manifest = "{{ internal_modules_path }}/{{ module.name }}/{{ test.path }}/{{ test.file }}"
        result = self.env.execute_cmd("%s '%s'" % (self.puppet_apply, manifest))
        self.assertIn(result, [0, 2])
        {%- if test.spec_file %}
        result = self.env.execute_cmd('rspec -f doc --color "{{ internal_modules_path }}/{{ module.name }}/{{ test.spec_file }}"')
        self.assertEqual(result, 0)
        {%- elif test.verify_file %}
        result = self.env.execute_cmd('{{ internal_modules_path }}/{{ module.name }}/{{ test.verify_file }}')
        self.assertEqual(result, 0)
        {%- endif %}
{% endfor %}

    def tearDown(self):
        self.env.revert_snapshot_env("before_test")

if __name__ == '__main__':
    unittest.main()

{# Enable this to get a debug list with all template values
{% include 'debug_template.txt' %}
#}
