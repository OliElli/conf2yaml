#!/usr/bin/env python

from ciscoconfparse import CiscoConfParse
from os import walk, makedirs, listdir
from os.path import isfile, join, splitext, exists
import re
import yaml
import sys
import pprint

# parse takes a filename and subdirectory and creates the corresponding yaml/sdir/filename.yml file
def parse(filename, sdir):
  parse = CiscoConfParse('configurations/' + sdir + '/' + filename)     # Load in source configuration file
  output_config = {}                                                    # Create master dict for output data

  # switch stacks
  stacks = parse.find_objects(r'switch [0-9]+ provision (.*)')
  if stacks:
    output_config['switch_stack'] = []
    for line in stacks:
      stack = line.re_match(r'switch [0-9]+ provision (.*)')
      output_config['switch_stack'].append(stack)

  # Interfaces
  interfaces = parse.find_objects(r'interface')     # Create interfaces object
  if interfaces:
    output_config['interfaces'] = []            # Create list of interfaces
    for interface in interfaces:
      # dict for this particular interface
      interface_dict = {}

      # Insert interface name
      interface_name = interface.re_match(r'^interface (\S+)$')
      if interface_name:
          interface_dict['name'] = interface_name

      # switchport

      # Find list of interfaces with "switchport" config
      switchport_interfaces = interface.re_search_children(r'switchport')
      if switchport_interfaces:

        # Create switchport dict if it does not yet exist
        if not 'switchport' in interface_dict:
          interface_dict['switchport'] = {}

        for line in switchport_interfaces:

          # access vlan
          access_vlan = line.re_match(r' switchport access vlan (\S+)')
          if access_vlan:
            interface_dict['switchport']['access_vlan'] = access_vlan

          # switchport mode
          switchport_mode = line.re_match(r'^ switchport mode (\S+)$')
          if switchport_mode:
            interface_dict['switchport']['mode'] = switchport_mode

          # port-security
          port_sec = line.re_search(r'^ switchport port-security$')
          if port_sec:
            interface_dict['switchport']['port_security'] = True

          # switchport trunk
          switchport_trunk = line.re_search(r'^ switchport trunk.*$')
          if switchport_trunk:

            # Create the trunk dict if it does not yet exist
            if not 'trunk' in interface_dict['switchport']:
              interface_dict['switchport']['trunk'] = {}

            # native vlan
            native_vlan = line.re_match(r'^ switchport trunk native vlan (\S+)$')
            if native_vlan:
              interface_dict['switchport']['trunk']['native_vlan'] = native_vlan

            # allowed vlan
            allowed_vlan = line.re_match(r'^ switchport trunk allowed vlan (\S+)$')
            if allowed_vlan:
              interface_dict['switchport']['trunk']['allowed_vlan'] = allowed_vlan

            # trunk encapsulation
            encapsulation = line.re_match(r'^ switchport trunk encapsulation (.+)$')
            if encapsulation:
              interface_dict['switchport']['trunk']['encapsulation'] = encapsulation

      # spanning-tree
      spanning_tree = interface.re_search_children(r'spanning-tree')
      if spanning_tree:
        # Create spanning-tree dict if it does not yet exist
        if not 'spanning_tree' in interface_dict:
          interface_dict['spanning_tree'] = {}

        for line in spanning_tree:

          # portfast
          portfast = line.re_search(r'^ spanning-tree portfast$')
          if portfast:
            interface_dict['spanning_tree']['portfast'] = True

          # guard_root
          guard_root = line.re_search(r'^ spanning-tree guard root$')
          if guard_root:
            interface_dict['spanning_tree']['guard_root'] = True

      # ip
      ip = interface.re_search_children(r'^ ip ')
      if ip:
        # Create ip dict if it does not yet exist
        if not 'ip' in interface_dict:
          interface_dict['ip'] = {}

        for line in ip:
          # ip address
          ip_address = line.re_search(r'^ ip address (.*)$')
          if ip_address:
            interface_dict['ip']['address'] = ip_address

          # ip access_group
          access_group = re.match('^ ip access-group (\S+) (\S+)$', line.text)
          if access_group:
            # Create access_group sub-dict if it does not yet exist
            if not 'access_group' in interface_dict['ip']:
              interface_dict['ip']['access_group'] = {}

            interface_dict['ip']['access_group'][access_group.group(1)] = access_group.group(2)

          # ip dhcp snooping trust
          dhcp_snooping_trust = line.re_search(r'^ ip dhcp snooping trust$')
          if dhcp_snooping_trust:
            interface_dict['ip']['dhcp_snooping_trust'] = True

      # no ip
      no_ip = interface.re_search_children(r'^ no ip ')

      if no_ip:
        # Create ip dict if it does not yet exist
        if not 'ip' in interface_dict:
          interface_dict['ip'] = {}

        for line in no_ip:

          # no ip address
          no_ip = line.re_search(r'^ no ip address$')
          if no_ip:
            interface_dict['ip']['ip_address_disable'] = True

          # no ip route cache
          no_route_cache = line.re_search(r'^ no ip route-cache$')
          if no_route_cache:
            interface_dict['ip']['route_cache_disable'] = True

          # no ip mroute-cache
          no_mroute_cache = line.re_search(r'^ no ip mroute-cache$')
          if no_mroute_cache:
            interface_dict['ip']['mroute_cache_disable'] = True

      # ipv6
      ipv6 = interface.re_search_children(r'^ ipv6 ')
      if ipv6:
        if not 'ipv6' in interface_dict:
          interface_dict['ipv6'] = []

        for line in ipv6:
          # ra guard
          ra_guard = line.re_search(r'^ ipv6 nd raguard$')
          if ra_guard:
            interface_dict['ipv6'].append('ra_guard')

          # ipv6 snooping
          ra_guard = line.re_search(r'^ ipv6 snooping$')
          if ra_guard:
            interface_dict['ipv6'].append('ipv6_snooping')

          # ipv6 dhcp guard
          ra_guard = line.re_search(r'^ ipv6 dhcp guard$')
          if ra_guard:
            interface_dict['ipv6'].append('ipv6_dhcp_guard')

      # misc
      misc = interface.re_search_children(r'.*')

      if misc:
        for line in misc:

          # description
          interface_description = line.re_match(r'^ description (\S+)$')
          if interface_description:
            interface_dict['description'] = interface_description

          # power inline police
          power_inline_police = line.re_search(r'^ power inline police$')
          if power_inline_police:
            interface_dict['power_inline_police'] = True

          # cdp disable
          cdp_disable = line.re_search(r'^ no cdp enable$')
          if cdp_disable:
            interface_dict['cdp_disable'] = True

          # shutdown
          shutdown = line.re_search(r'^ shutdown$')
          if shutdown:
            interface_dict['shutdown'] = True

          # vrf forwarding
          vrf = line.re_match(r'^ vrf forwarding (.+)$')
          if vrf:
            interface_dict['vrf'] = vrf

          # negotiation
          negotiation = line.re_match(r'^ negotiation (.+)$')
          if negotiation:
            interface_dict['negotiation'] = negotiation

          # keepalive disable
          keepalive_disable = line.re_search(r'^ no keepalive$')
          if keepalive_disable:
            interface_dict['keepalive_disable'] = True

      # Append the completed interface dict to the interfaces list
      output_config['interfaces'].append(interface_dict)

  # IP Config Elements
  ip_config = parse.find_objects(r'ip')
  if ip_config:
    # Create ip dict if it does not yet exist
    if not 'ip' in output_config:
      output_config['ip'] = {}

    for line in ip_config:

      # ip dhcp snooping
      dhcp_snooping = line.re_search(r'^ip dhcp snooping$')
      if dhcp_snooping:
        output_config['ip']['dhcp_snooping'] = True

      # ip default gateway
      default_gateway = line.re_match(r'^ip default-gateway (\S+)$')
      if default_gateway:
        output_config['ip']['default_gateway'] = default_gateway

  # Banner
  banner = parse.find_blocks(r'banner')
  if banner:
    # Create banner dict if it does not yet exist
    if not 'banner' in output_config:
      output_config['banner'] = []

    for line in banner:
      first_line = re.search(r'^banner motd (.*)$', line)
      if first_line:
        output_config['banner'].append(first_line.group(1))
      else:
        output_config['banner'].append(line)

  # acl
  acl = parse.find_blocks(r'access-list')
  if acl:
    if not 'acl' in output_config:
      output_config['acl'] = []

    for line in acl:
      acl_line = re.search(r'^access-list 10 permit (172.*)$', line)
      if acl_line:
        output_config['acl'].append(acl_line.group(1))

  # snmp-server
  snmp = parse.find_blocks(r'snmp-server')
  if snmp:
    # Create snmp dict if it does not yet exist
    if not 'snmp' in output_config:
      output_config['snmp'] = {}

    for line in snmp:

      # community string
      snmp_community = re.match(r'^snmp-server community (\S+)', line)
      if snmp_community:
        output_config['snmp']['community'] = snmp_community.group(1)

      # location
      snmp_location = re.match(r'^snmp-server location (.*)$', line)
      if snmp_location:
        output_config['snmp']['location'] = snmp_location.group(1)

      # contact
      snmp_contact = re.match(r'^snmp-server contact (.*)$', line)
      if snmp_contact:
        output_config['snmp']['contact'] = snmp_contact.group(1)

  # vtp
  vtp = parse.find_lines(r'vtp')
  if vtp:
    vtp_mode = re.match(r'vtp mode (\S+)',vtp[0])
    if vtp_mode:
      output_config['vtp_mode'] = vtp_mode.group(1)

  # vlans
  vlans = parse.find_objects('^vlan [0-9]+')
  if vlans:
    # Create vlans dict if it does not yet exist
    if not 'vlans' in output_config:
      output_config['vlans'] = []

    for vlan in vlans:
      vlan_dict = {}

      # vlan number
      vlan_number = re.match('^vlan (\d.*)$', vlan.text)
      if vlan_number:
        vlan_dict['number'] = vlan_number.group(1)

      # vlan name
      vlan_name = vlan.re_search_children(r'name')
      if vlan_name:
        name = vlan_name[0].re_match(r' name (\S+)')
        vlan_dict['name'] = name

      # Append the completed vlan dict
      output_config['vlans'].append(vlan_dict)

  # certificates
  certificate_chain = parse.find_lines('^crypto pki certificate chain')
  if certificate_chain:
    for line in certificate_chain:
      certificate_chain_search = re.match('^crypto pki certificate chain (\S+)', line)
      output_config['crypto_chain_id'] = certificate_chain_search.group(1)

  # radius server config
  radius_servers = parse.find_objects('radius server')
  if radius_servers:
    output_config['radius_servers'] = True

  # Screen output
  # print
  # print(sdir + '/' + filename + ' YAML Output:')
  # print
  # print yaml.dump(output_config, default_flow_style=False, explicit_start=True)
  print('Outputing ' + filename + ' YAML')

  # Make sure the directory we're trying to write to exists. Create it if it doesn't
  out_path = 'yaml/' + sdir + '/'
  if not exists(out_path):
    makedirs(out_path)

  # Write foo.yml to the subdir in yaml/ that corresponds to the dir where we got the input file in configurations/
  with open(out_path + splitext(filename)[0] + '.nwid.bris.ac.uk.yml', 'w') as outfile:
    yaml.dump(output_config, outfile, default_flow_style=False, explicit_start=True)

root_path = 'configurations/'       # specify root directory
subdirs = walk(root_path).next()[1]   # obtain all subdirectories
subdirs.append('');           # add root directory

for s in subdirs:
  files = [f for f in listdir(root_path + s) if isfile(join(root_path + s, f))]
  for f in files:
    if f != '.gitignore':       # let's not try to parse gitignores
      parse(f, s)
