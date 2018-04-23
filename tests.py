import unittest
from conf2yaml import convert_to_yaml
from ciscoconfparse import CiscoConfParse
from pyfakefs import fake_filesystem_unittest
from test_data import *

class test_suite(unittest.TestCase):
    def test_interface_name_identification(self):
        with fake_filesystem_unittest.Patcher() as patcher:
            patcher.fs.create_file('/mock', contents=test_interface_name_identification["input"])
            self.assertEqual(convert_to_yaml(CiscoConfParse('/mock')), test_interface_name_identification["output"])

    def test_interface_cdp_status(self):
        with fake_filesystem_unittest.Patcher() as patcher:
            patcher.fs.create_file('/mock', contents=test_interface_cdp_status["input"])
            self.assertEqual(convert_to_yaml(CiscoConfParse('/mock')), test_interface_cdp_status["output"])

    def test_interface_switchport_access_vlan(self):
        with fake_filesystem_unittest.Patcher() as patcher:
            patcher.fs.create_file('/mock', contents=test_interface_switchport_access_vlan["input"])
            self.assertEqual(convert_to_yaml(CiscoConfParse('/mock')), test_interface_switchport_access_vlan["output"])

    def test_interface_switchport_mode(self):
        with fake_filesystem_unittest.Patcher() as patcher:
            patcher.fs.create_file('/mock', contents=test_interface_switchport_mode["input"])
            self.assertEqual(convert_to_yaml(CiscoConfParse('/mock')), test_interface_switchport_mode["output"])

    def test_interface_switchport_port_security(self):
        with fake_filesystem_unittest.Patcher() as patcher:
            patcher.fs.create_file('/mock', contents=test_interface_switchport_port_security["input"])
            self.assertEqual(convert_to_yaml(CiscoConfParse('/mock')), test_interface_switchport_port_security["output"])

    def test_interface_power_inline_police(self):
        with fake_filesystem_unittest.Patcher() as patcher:
            patcher.fs.create_file('/mock', contents=test_interface_power_inline_police["input"])
            self.assertEqual(convert_to_yaml(CiscoConfParse('/mock')), test_interface_power_inline_police["output"])

    def test_interface_spanning_tree(self):
        with fake_filesystem_unittest.Patcher() as patcher:
            patcher.fs.create_file('/mock', contents=test_interface_spanning_tree["input"])
            self.assertEqual(convert_to_yaml(CiscoConfParse('/mock')), test_interface_spanning_tree["output"])


if __name__ == '__main__':
    unittest.main()