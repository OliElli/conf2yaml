#
# Define the file input and expected output for each test case
#
test_interface_name_identification = {
    "input": "interface GigabitEthernet1/0/1",
    "output": """---
interfaces:
- name: GigabitEthernet1/0/1\n"""
}

test_interface_cdp_status = {
    "input":
"""interface GigabitEthernet1/0/1
 no cdp enable""",
    "output":
"""---
interfaces:
- cdp_disable: true
  name: GigabitEthernet1/0/1\n"""
}

test_interface_switchport_access_vlan = {
    "input": """interface GigabitEthernet1/0/1
 switchport access vlan 4""",
    "output": """---
interfaces:
- name: GigabitEthernet1/0/1
  switchport:
    access_vlan: '4'\n"""
}

test_interface_switchport_mode = {
    "input": """interface GigabitEthernet1/0/1
 switchport mode access""",
    "output": """---
interfaces:
- name: GigabitEthernet1/0/1
  switchport:
    mode: access\n"""
}

test_interface_switchport_port_security = {
    "input": """interface GigabitEthernet1/0/1
 switchport port-security""",
    "output": """---
interfaces:
- name: GigabitEthernet1/0/1
  switchport:
    port_security: true\n"""
}

test_interface_power_inline_police = {
    "input": """interface GigabitEthernet1/0/1
 power inline police""",
    "output": """---
interfaces:
- name: GigabitEthernet1/0/1
  power_inline_police: true\n"""
}

test_interface_spanning_tree = {
    "input": """interface GigabitEthernet1/0/1
 spanning-tree portfast
 spanning-tree guard root""",
    "output": """---
interfaces:
- name: GigabitEthernet1/0/1
  spanning_tree:
    guard_root: true
    portfast: true\n"""
}