#!/usr/bin/env python

from ciscoconfparse import CiscoConfParse
from os import walk, makedirs, listdir
from os.path import isfile, join, splitext, exists
import re
import yaml
import sys
import pprint

def match_multi_line(collection, str):
  for j in collection.children:
    if re.match(str, j.text):
      return "True"
      break

def match_single_line(j, str, capture):
  match = re.match(str, j.text)
  if match:
    return (match.group(1) if capture else "True")

def match_single_line_many(j, str, capture):
  match = re.search(str, j.text)
  if match:
    return match.groups()

def search_multi_line(collection, str, capture):
  for j in collection:
    match = re.search(str, j)
    if match:
      return (match.group(1) if capture else "True")

def search_single_line(i, str, capture):
  match = re.search(str, i.text)
  if match:
    return (match.group(1) if capture else "True")

# parse takes a filename and subdirectory and creates the corresponding yaml/sdir/filename.yml file
def parse(filename, sdir):
  p = CiscoConfParse('configurations/' + sdir + '/' + filename)     # Load in source configuration file
  output_config = {}                                                # Create master dict for output data

  # switch stacks
  switch_stack = p.find_objects('^switch [0-9]+ provision')
  if switch_stack:
    # Create switch stack sub-dict
    if not 'switch_stack' in output_config.keys():
      output_config['switch_stack'] = []

    for i in switch_stack:
      provision = match_single_line_many(i, '^switch ([0-9]+) provision (.+)$', True)
      if provision:
        output_config['switch_stack'].append(provision[1])

  # Interfaces
  interfaces = p.find_objects(r'interface')     # Create interfaces object
  if interfaces:
    output_config['interfaces'] = []            # Create list of interfaces
    for i in interfaces:
      interface_dict = {}

      # Insert interface name
      interface_name = search_single_line(i, '^interface (\S+)$', True)
      if interface_name:
        interface_dict['name'] = interface_name

      # switchport
      switchport = match_multi_line(i, '^ switchport.*$')
      if switchport:

        # Create switchport sub-dict
        interface_dict['switchport'] = {}

        for j in i.children:

          # access vlan
          access_vlan = match_single_line(j, '^ switchport access vlan (\S+)$', True)
          if access_vlan:
            interface_dict['switchport']['access_vlan'] = str(access_vlan)

          # switchport mode
          mode = match_single_line(j, '^ switchport mode (\S+)$', True)
          if mode:
            interface_dict['switchport']['mode'] = mode

          # port-security
          port_sec = match_single_line(j, '^ switchport port-security$', False)
          if port_sec:
            interface_dict['switchport']['port_security'] = 'True'

          # switchport trunk
          switchport_trunk = match_multi_line(i, '^ switchport trunk.*$')
          if switchport_trunk:
            interface_dict['switchport']['trunk'] = {}

        for j in i.children:

          # native vlan
          native_vlan = match_single_line(j, '^ switchport trunk native vlan (\S+)$', True)
          if native_vlan:
            interface_dict['switchport']['trunk']['native_vlan'] = native_vlan

          # allowed vlan
          allowed_vlan = match_single_line(j, '^ switchport trunk allowed vlan (\S+)$', True)
          if allowed_vlan:
            interface_dict['switchport']['trunk']['allowed_vlan'] = allowed_vlan

          # trunk encapsulation
          encapsulation = match_single_line(j, '^ switchport trunk encapsulation (.+)$', True)
          if encapsulation:
            interface_dict['switchport']['trunk']['encapsulation'] = encapsulation


      # spanning-tree
      spanning_tree = match_multi_line(i, '^ spanning-tree.*$')
      if spanning_tree:
        # Create spanning-tree sub-dict
        if not 'spanning_tree' in interface_dict.keys():
          interface_dict['spanning_tree'] = {}

        for j in i.children:
          # portfast
          portfast = match_single_line(j, '^ spanning-tree portfast$', False)
          if portfast:
            interface_dict['spanning_tree']['portfast'] = portfast
          # guard_root
          guard_root = match_single_line(j, '^ spanning-tree guard root$', False)
          if guard_root:
            interface_dict['spanning_tree']['guard_root'] = guard_root

      # ip
      ip = match_multi_line(i, '^ ip .*$')
      if ip:
        # Create ip sub-dict
        if not 'ip' in interface_dict.keys():
          interface_dict['ip'] = {}

        for j in i.children:

          # ip address
          ip_address = match_single_line(j, '^ ip address (.*)$', True)
          if ip_address:
            interface_dict['ip']['address'] = ip_address
          # ip access_group
          access_group = match_single_line_many(j, '^ ip access-group (\S+) (\S+)$', True)
          if access_group:
            # Create access_group sub-dict
            interface_dict['ip']['access_group'] = {}
            interface_dict['ip']['access_group'][access_group[0]] = access_group[1]
          # ip dhcp snooping trust
          dhcp_snooping_trust = match_single_line(j, '^ ip dhcp snooping trust$', False)
          if dhcp_snooping_trust:
            interface_dict['ip']['dhcp_snooping_trust'] = dhcp_snooping_trust

      # no ip
      no_ip = match_multi_line(i, '^ no ip .*$')
      if no_ip:
        # Create ip sub-dict
        if not 'ip' in interface_dict.keys():
          interface_dict['ip'] = {}

          #interface_dict['ip'] = {}

        for j in i.children:

          # no ip address
          no_ip = match_single_line(j, '^ no ip address$', False)
          if no_ip:
            interface_dict['ip']['ip_address_disable'] = no_ip

          # no ip route cache
          no_route_cache = match_single_line(j, '^ no ip route-cache$', False)
          if no_route_cache:
            interface_dict['ip']['route_cache_disable'] = no_route_cache

          # no ip mroute-cache
          no_mroute_cache = match_single_line(j, '^ no ip mroute-cache$', False)
          if no_mroute_cache:
            interface_dict['ip']['mroute_cache_disable'] = no_mroute_cache

      # misc
      for j in i.children:

        # description
        interface_description = match_single_line(j, '^ description (.*)$', True)
        if interface_description:
          interface_dict['description'] = interface_description

        # power inline police
        power_inline_police = match_single_line(j, '^ power inline police$', False)
        if power_inline_police:
          interface_dict['power_inline_police'] = power_inline_police

        # cdp disable
        cdp_disable = match_single_line(j, '^ no cdp enable$', False)
        if cdp_disable:
          interface_dict['cdp_disable'] = cdp_disable

        # shutdown
        shutdown = match_single_line(j, '^ shutdown$', False)
        if shutdown:
          interface_dict['shutdown'] = shutdown

        # vrf forwarding
        vrf = match_single_line(j, '^ vrf forwarding (.+)$', True)
        if vrf:
          interface_dict['vrf'] = vrf

        # negotiation
        negotiation = match_single_line(j, '^ negotiation (.+)$', True)
        if negotiation:
          interface_dict['negotiation'] = negotiation

        # keepalive disable
        keepalive_disable = match_single_line(j, '^ no keepalive$', False)
        if keepalive_disable:
          interface_dict['keepalive_disable'] = keepalive_disable

      # Append the completed interface dict to the interfaces list
      output_config['interfaces'].append(interface_dict)

  # IP Config Elements
  ip_config = p.find_objects(r'ip')
  if ip_config:
    # Create ip dict
    output_config['ip'] = {}
    for i in ip_config:
      # ip dhcp snooping
      dhcp_snooping = match_single_line(i, '^ip dhcp snooping$', False)
      if dhcp_snooping:
        output_config['ip']['dhcp_snooping'] = dhcp_snooping
      default_gateway = match_single_line(i, '^ip default-gateway (\S+)$', True)
      if default_gateway:
        output_config['ip']['default_gateway'] = default_gateway

  # Banner
  banner = p.find_blocks(r'banner')
  if banner:
    # Create banner dict
    output_config['banner'] = []

    for i in banner:
      match = re.search('^banner motd (.*)$', i)
      if match:
        output_config['banner'].append(match.group(1))
      else:
        output_config['banner'].append(i)

  # acl
  acl = p.find_blocks(r'access-list')
  if acl:
    acl_line = search_multi_line(acl, '^access-list 10 permit (172.*)$', True)
    if acl_line:
      output_config['acl'] = acl_line

  # snmp-server
  snmp = p.find_blocks(r'snmp-server')
  if snmp:
    # Create snmp dict
    output_config['snmp'] = {}

    snmp_community = search_multi_line(snmp, '^snmp-server community (\S+)', True)
    if snmp_community:
      output_config['snmp']['community'] = snmp_community
    snmp_location = search_multi_line(snmp, '^snmp-server location (.*)$', True)
    if snmp_location:
      output_config['snmp']['location'] = snmp_location
    snmp_contact = search_multi_line(snmp, '^snmp-server contact (.*)$', True)
    if snmp_contact:
      output_config['snmp']['contact'] = snmp_contact

  # vtp
  vtp = p.find_blocks(r'vtp')
  if vtp:
    vtp_mode = search_multi_line(vtp, 'vtp mode (\S+)', True)
    if vtp_mode:
      output_config['vtp_mode'] = vtp_mode

  # vlans
  vlans = p.find_objects('^vlan')
  if vlans:
    output_config['vlans'] = []
    for i in vlans:
      match = re.match('^vlan (\d.*)$', i.text)
      if match:
        # Create vlans dict
        vlan_output = {}
        vlan_output['number'] = match.group(1)
        match2 = i.re_search_children(r" name ")
        if match2:
          for j in match2:
            match3 = re.match('^ name (\S+)$', j.text)
            if match3:
              vlan_output['name'] = match3.group(1)
        # Append the completed vlans dict to the output_config list
        output_config['vlans'].append(vlan_output)

  # certificates
  certificate_chain = p.find_lines('^crypto pki certificate chain')
  if certificate_chain:
    for line in certificate_chain:
      certificate_chain_search = re.match('^crypto pki certificate chain (\S+)', line)
      output_config['crypto_chain_id'] = certificate_chain_search.group(1)

  # radius
  radius_servers = p.find_objects('radius server')
  if radius_servers:
    output_config['radius_servers'] = []
    for line in radius_servers:
      match = re.match('radius server (\S+)', line.text)
      output_config['radius_servers'].append(match.group(1))

    #   search_term = 'radius server ' + radius_server_name
      address_line = p.find_children_w_parents(line.text, 'address ipv4')
      if address_line:
        match = re.match(' address ipv4 (\S+) auth-port ([0-9]+) acct-port ([0-9]+)', address_line[0])
        if match:
          address = match.group(1)
          auth_port = match.group(2)
          acct_port = match.group(3)

          print('DEBUG')
          print(address)
          print(auth_port)
          print(acct_port)
          sys.exit





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
