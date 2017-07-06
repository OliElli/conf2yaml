#!/usr/bin/env python
from ciscoconfparse import CiscoConfParse
import re

# Load in source configuration file
config = 'configurations/tests1.svn'
p = CiscoConfParse(config)

print('---') # Mark beginning of output

def match_collection(collection, str, output):
    for j in collection.children:
        if re.match(str, j.text):
            print(output)
            break

def match_single(j, str, output, addGroup, suffix=""):
    match = re.match(str, j.text)
    if match:
        if not isinstance(output, list):
            print(output + (match.group(1) if addGroup else "") + suffix)
        else:
            print(output[0] + match.group(1) + output[1] + match.group(2))
        
def search_collection(collection, str, output, addGroup, suffix=""):
    for j in collection:
        match = re.search(str, j)
        if match:
            print(output + (match.group(1) if addGroup else "") + suffix)
            
def search_single(i, str, output, addGroup, suffix=""):
    match = re.search(str, i.text)
    if match:
        print(output + (match.group(1) if addGroup else "") + suffix)

# Create interfaces object
ints = p.find_objects(r'interface')
        
# Iterate interfaces
if ints:
    print('interfaces:')
    for i in ints:
        search_single(i, '^interface (\S+)$', '  - name ', True, ':')
        match_collection(i, '^ switchport.*$', '    switchport:')                                   # switchport
        
        for j in i.children:
            match_single(j, '^ switchport access vlan (\S+)$', '      access_vlan: ', True)         # access vlan
            match_single(j, '^ switchport mode (\S+)$', '      mode: ', True)                       # switchport mode
            match_single(j, '^ switchport port-security$', '      port_security: "True"', False)    # port security
                
        match_collection(i, '^ switchport trunk.*$', '      trunk:')                                # switchport trunk
            
        for j in i.children:
            match_single(j, '^ switchport trunk native vlan (\S+)$', '        native_vlan: ', True)
            match_single(j, '^ switchport trunk allowed vlan (\S+)$', '        allowed_vlan: ', True)

        match_collection(i, '^ spanning-tree.*$', '    spanning_tree:')                             # spanning-tree
        
        for j in i.children:
            match_single(j, '^ spanning-tree portfast$', '      portfast: "True"', False)           # spanning-tree portfast
            match_single(j, '^ spanning-tree guard root$', '      guard_root: "True"', False)       # spanning-tree guard root

        match_collection(i, '^ .* ip .*$', '    ip:')                                               # ip
        
        for j in i.children:
            match_single(j, '^ no ip address$', '      ip_address_disable: "True"', False)                                                  # no ip address
            match_single(j, '^ no ip route-cache$', '      route_cache_disable: "True"', False)                                             # no ip route-cache
            match_single(j, '^ ip address (.*)$', '      address: ', True)                                                                  # ip address
            match_single(j, '^ ip access-group (\S+) (\S+)$', ['      access_group:\n        acl_id: ', '\n        direction: '], False, "")# ip access-group
            match_single(j, '^ ip dhcp snooping trust$', '      dhcp_snooping_trust: "True"', False)                                        # ip access-group

        # misc
        for j in i.children:
            match_single(j, '^ power inline police$', '    power_inline_police: "True"', False)     # power inline police
            match_single(j, '^ no cdp enable$', '    cdp_disable: "True"', False)                   # no cdp enable
            match_single(j, '^ shutdown$', '    shutdown: "True"', False)                           # shutdown

# IP Config Elements
ip_config = p.find_objects(r'ip')
if ip_config:
    print('ip:')
    for j in ip_config:
        match_single(j, '^ip dhcp snooping$', '  dhcp_snooping: "True"', False)                     # ip dhcp snooping
        match_single(j, '^ip default-gateway (\S+)$', '  default_gateway: ', True)                  # ip default gateway

# Banner
banner = p.find_blocks(r'banner')
if banner:
    print('banner:')
    for i in banner:
        match = re.search('^banner motd (.*)$',i)
        if match:
            print('  motd:')
            print('    - "' + match.group(1) + '"')
        else:
            print('    - "' + i + '"')

# acl
acl = p.find_blocks(r'access-list')
if acl:
    print('acl:')
    search_collection(acl, '^access-list 10 permit (172.*)$', '  - ', True)

# snmp-server
snmp = p.find_blocks(r'snmp-server')
if snmp:
    print('snmp:')
    search_collection(snmp, '^snmp-server location (.*)$', '  location: ', True)
    search_collection(snmp, '^snmp-server contact (.*)$', '  contact: ', True)

# vtp
vtp = p.find_blocks(r'vtp')
if vtp:
    print('vtp:')
    search_collection(vtp, 'vtp mode (\S+)', '  mode: "', True, '"')

# vlans
vlans = p.find_objects('^vlan')
if vlans:
    print('vlans:')
    for i in vlans:
        search_single(i, '^vlan (\d.*)$', '  - number: ', True)
        
        match = i.re_search_children(r" name ")
        if match:
            for j in match:
                search_single(j, r'name (.*)', '    name: ', True)
