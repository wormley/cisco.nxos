# (c) 2016 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish

from __future__ import absolute_import, division, print_function


__metaclass__ = type

from ansible_collections.cisco.nxos.plugins.modules import nxos_pim_interface
from ansible_collections.cisco.nxos.tests.unit.compat.mock import patch

from .nxos_module import TestNxosModule, load_fixture, set_module_args


class TestNxosIPInterfaceModule(TestNxosModule):
    module = nxos_pim_interface

    def setUp(self):
        super(TestNxosIPInterfaceModule, self).setUp()

        self.mock_get_config = patch(
            "ansible_collections.cisco.nxos.plugins.modules.nxos_pim_interface.get_config",
        )
        self.get_config = self.mock_get_config.start()

        self.mock_load_config = patch(
            "ansible_collections.cisco.nxos.plugins.modules.nxos_pim_interface.load_config",
        )
        self.load_config = self.mock_load_config.start()

        self.mock_run_commands = patch(
            "ansible_collections.cisco.nxos.plugins.modules.nxos_pim_interface.run_commands",
        )
        self.run_commands = self.mock_run_commands.start()

    def tearDown(self):
        super(TestNxosIPInterfaceModule, self).tearDown()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_run_commands.stop()

    def load_fixtures(self, commands=None, device=""):
        module_name = self.module.__name__.rsplit(".", 1)[1]

        def load_from_file(*args, **kwargs):
            module, commands = args
            output = list()

            for command in commands:
                if type(command) is dict:
                    command = command["command"]
                filename = str(command).split(" | ", 1)[0].replace(" ", "_").replace("/", "_")
                output.append(load_fixture(module_name, filename))
            return output

        self.get_config.return_value = load_fixture(module_name, "config.cfg")
        self.load_config.return_value = None
        self.run_commands.side_effect = load_from_file

    def test_nxos_pim_interface_present(self):
        set_module_args(
            dict(
                interface="eth2/1",
                dr_prio=10,
                hello_interval=40,
                sparse=True,
                border=False,
            ),
        )
        self.execute_module(
            changed=True,
            commands=[
                "interface eth2/1",
                "ip pim dr-priority 10",
                "ip pim hello-interval 40000",
                "ip pim sparse-mode",
            ],
        )

    def test_nxos_pim_interface_jp(self):
        set_module_args(
            dict(
                interface="eth2/1",
                jp_policy_in="JPIN",
                jp_policy_out="JPOUT",
                jp_type_in="routemap",
                jp_type_out="routemap",
            ),
        )
        self.execute_module(
            changed=True,
            commands=[
                "interface eth2/1",
                "ip pim jp-policy JPOUT out",
                "ip pim jp-policy JPIN in",
            ],
        )

    def test_nxos_pim_interface_default(self):
        set_module_args(dict(interface="eth2/1", state="default"))
        self.execute_module(changed=False, commands=[])

    def test_nxos_pim_interface_ip_absent(self):
        set_module_args(dict(interface="eth2/1", state="absent"))
        self.execute_module(changed=False, commands=[])


class TestNxosPimInterfaceBfdModule(TestNxosModule):
    module = nxos_pim_interface

    def setUp(self):
        super(TestNxosPimInterfaceBfdModule, self).setUp()

        self.mock_get_interface_mode = patch(
            "ansible_collections.cisco.nxos.plugins.modules.nxos_pim_interface.get_interface_mode",
        )
        self.get_interface_mode = self.mock_get_interface_mode.start()

        self.mock_get_config = patch(
            "ansible_collections.cisco.nxos.plugins.modules.nxos_pim_interface.get_config",
        )
        self.get_config = self.mock_get_config.start()

        self.mock_load_config = patch(
            "ansible_collections.cisco.nxos.plugins.modules.nxos_pim_interface.load_config",
        )
        self.load_config = self.mock_load_config.start()

        self.mock_run_commands = patch(
            "ansible_collections.cisco.nxos.plugins.modules.nxos_pim_interface.run_commands",
        )
        self.run_commands = self.mock_run_commands.start()

    def tearDown(self):
        super(TestNxosPimInterfaceBfdModule, self).tearDown()
        self.mock_get_interface_mode.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_run_commands.stop()

    def load_fixtures(self, commands=None, device=""):
        self.load_config.return_value = None

    def test_bfd_1(self):
        # default (None) -> enable
        self.get_config.return_value = None
        set_module_args(dict(interface="eth2/1", bfd="enable"))
        self.execute_module(changed=True, commands=["interface eth2/1", "ip pim bfd-instance"])

        # default (None) -> disable
        set_module_args(dict(interface="eth2/1", bfd="disable"))
        self.execute_module(
            changed=True,
            commands=["interface eth2/1", "ip pim bfd-instance disable"],
        )

        # default (None) -> default (None) (idempotence)
        set_module_args(dict(interface="eth2/1", bfd="default"))
        self.execute_module(changed=False)

        # default (None) -> interface state 'default'
        set_module_args(dict(interface="Ethernet9/3", state="default"))
        self.execute_module(changed=False)

        # default (None) -> interface state 'absent'
        set_module_args(dict(interface="Ethernet9/3", state="absent"))
        self.execute_module(changed=False)

    def test_bfd_2(self):
        # From disable
        self.get_config.return_value = """
            interface Ethernet9/2
              ip pim bfd-instance disable
        """
        # disable -> enable
        set_module_args(dict(interface="Ethernet9/2", bfd="enable"))
        self.execute_module(
            changed=True,
            commands=["interface Ethernet9/2", "ip pim bfd-instance"],
        )

        # disable -> disable (idempotence)
        set_module_args(dict(interface="Ethernet9/2", bfd="disable"))
        self.execute_module(changed=False)

        # disable -> default (None)
        set_module_args(dict(interface="Ethernet9/2", bfd="default"))
        self.execute_module(
            changed=True,
            commands=["interface Ethernet9/2", "no ip pim bfd-instance"],
        )
        # disable -> interface state 'default'
        set_module_args(dict(interface="Ethernet9/3", state="default"))
        self.execute_module(
            changed=True,
            commands=["interface Ethernet9/3", "no ip pim bfd-instance"],
        )

        # disable -> interface state 'absent'
        set_module_args(dict(interface="Ethernet9/3", state="absent"))
        self.execute_module(
            changed=True,
            commands=["interface Ethernet9/3", "no ip pim bfd-instance"],
        )

    def test_bfd_3(self):
        # From enable
        self.get_config.return_value = """
            interface Ethernet9/2
              ip pim bfd-instance
        """
        # enable -> disabled
        set_module_args(dict(interface="Ethernet9/3", bfd="disable"))
        self.execute_module(
            changed=True,
            commands=["interface Ethernet9/3", "ip pim bfd-instance disable"],
        )

        # enable -> enable (idempotence)
        set_module_args(dict(interface="Ethernet9/3", bfd="enable"))
        self.execute_module(changed=False)

        # enable -> default (None)
        set_module_args(dict(interface="Ethernet9/3", bfd="default"))
        self.execute_module(
            changed=True,
            commands=["interface Ethernet9/3", "no ip pim bfd-instance"],
        )

        # enable -> interface state 'default'
        set_module_args(dict(interface="Ethernet9/3", state="default"))
        self.execute_module(
            changed=True,
            commands=["interface Ethernet9/3", "no ip pim bfd-instance"],
        )

        # enable -> interface state 'absent'
        set_module_args(dict(interface="Ethernet9/3", state="absent"))
        self.execute_module(
            changed=True,
            commands=["interface Ethernet9/3", "no ip pim bfd-instance"],
        )

    def test_bfd_4(self):
        self.get_config.return_value = """
            interface Ethernet9/2
              ip pim hello-interval 1000
        """
        # update hello-interval (as milliseconds)
        set_module_args(
            dict(
                interface="Ethernet9/2",
                hello_interval=1,
                hello_interval_ms=True,
            ),
        )
        self.execute_module(
            changed=True,
            commands=["interface Ethernet9/2", "ip pim hello-interval 1"],
        )

        # idempotent (as milliseconds)
        set_module_args(
            dict(
                interface="Ethernet9/2",
                hello_interval=1000,
                hello_interval_ms=True,
            ),
        )
        self.execute_module(changed=False, commands=[])

        # update hello-interval (default seconds)
        set_module_args(dict(interface="Ethernet9/2", hello_interval=2))
        self.execute_module(
            changed=True,
            commands=["interface Ethernet9/2", "ip pim hello-interval 2000"],
        )

        # idempotent (default seconds)
        set_module_args(dict(interface="Ethernet9/2", hello_interval=1))
        self.execute_module(changed=False, commands=[])
