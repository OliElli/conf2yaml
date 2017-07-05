#!/usr/bin/env python
from ciscoconfparse import CiscoConfParse
import re

# Load in source configuration file
config = 'configurations/tests1.svn'
p = CiscoConfParse(config)

print('---')

# Create interfaces object
ints = p.find_objects(r'interface')

# Iterate interfaces
if ints:
    print('interfaces:')
    for i in ints:
        match = re.search('^interface (\S+)$',i.text)
        print('  - name ' + match.group(1) + ':')

        # switchport
        for j in i.children:
            match = re.match('^ switchport.*$',j.text)
            if match:
                print('    switchport:')
                break
        for j in i.children:
            # access vlan
            match = re.match('^ switchport access vlan (\S+)$',j.text)
            if match:
                print('      access_vlan: ' + match.group(1))
            # switchport mode
            match = re.match('^ switchport mode (\S+)$',j.text)
            if match:
                print('      mode: ' + match.group(1))
            # port security
            match = re.match('^ switchport port-security$',j.text)
            if match:
                print('      port_security: "True"')
        # switchport trunk
        for j in i.children:
            match = re.match('^ switchport trunk.*$',j.text)
            if match:
                print('      trunk:')
                break
        for j in i.children:
            match = re.match('^ switchport trunk native vlan (\S+)$',j.text)
            if match:
                print('        native_vlan: ' + match.group(1))
            match = re.match('^ switchport trunk allowed vlan (\S+)$',j.text)
            if match:
                print('        allowed_vlan: ' + match.group(1))

        # spanning-tree
        for j in i.children:
            match = re.match('^ spanning-tree.*$',j.text)
            if match:
                print('    spanning_tree:')
                break
        for j in i.children:
            # spanning-tree portfast
            match = re.match('^ spanning-tree portfast$',j.text)
            if match:
                print('      portfast: "True"')
            # spanning-tree guard root
            match = re.match('^ spanning-tree guard root$',j.text)
            if match:
                print('      guard_root: "True"')

        # ip
        for j in i.children:
            match = re.match('^ .* ip .*$',j.text)
            if match:
                print('    ip:')
                break
        for j in i.children:
            # no ip address
            match = re.match('^ no ip address$',j.text)
            if match:
                print('      ip_address_disable: "True"')
            #  no ip route-cache
            match = re.match('^ no ip route-cache$',j.text)
            if match:
                print('      route_cache_disable: "True"')
            #  ip address
            match = re.match('^ ip address (.*)$',j.text)
            if match:
                print('      address: ' + match.group(1))
            #  ip access-group
            match = re.match('^ ip access-group (\S+) (\S+)$',j.text)
            if match:
                print('      access_group:\n        acl_id: ' + match.group(1) + '\n        direction: ' + match.group(2))
            #  ip access-group
            match = re.match('^ ip dhcp snooping trust$',j.text)
            if match:
                print('      dhcp_snooping_trust: "True"')

        # misc
        for j in i.children:
            # power inline police
            match = re.match('^ power inline police$',j.text)
            if match:
                print('    power_inline_police: "True"')
            # no cdp enable
            match = re.match('^ no cdp enable$',j.text)
            if match:
                print('    cdp_disable: "True"')
            # shutdown
            match = re.match('^ shutdown$',j.text)
            if match:
                print('    shutdown: "True"')

# IP Config Elements
ip_config = p.find_objects(r'ip')
if ip_config:
    print('ip:')
    for i in ip_config:
        # ip dhcp snooping
        match = re.search('^ip dhcp snooping$',i.text)
        if match:
            print('  dhcp_snooping: "True"')
        # ip default gateway
        match = re.search('^ip default-gateway (\S+)$',i.text)
        if match:
            print('  default_gateway: ' + match.group(1))

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
    for i in acl:
        match = re.search('^access-list 10 permit (172.*)$',i)
        if match:
            print('  - ' + match.group(1))

# snmp-server
snmp = p.find_blocks(r'snmp-server')
if snmp:
    print('snmp:')
    for i in snmp:
        match = re.search('^snmp-server location (.*)$',i)
        if match:
            print('  location: ' + match.group(1))
    for i in snmp:
        match = re.search('^snmp-server contact (.*)$',i)
        if match:
            print('  contact: ' + match.group(1))

# vtp
vtp = p.find_blocks(r'vtp')
if vtp:
    print('vtp:')
    for i in vtp:
        match = re.search('vtp mode (\S+)',i)
        if match:
            print('  mode: "' + match.group(1) + '"')

# vlans
vlans = p.find_objects('^vlan')
if vlans:
    print('vlans:')
    for i in vlans:
        match = re.search('^vlan (\d.*)$',i.text)
        if match:
            print('  - number: ' + match.group(1))
        match = i.re_search_children(r" name ")
        if match:
            for j in match:
                match2 = re.search(r'name (.*)',j.text)
                if match2:
                    print('    name: ' + match2.group(1))
