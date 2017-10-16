#!/usr/bin/env python
from ciscoconfparse import CiscoConfParse
from os import walk, makedirs, listdir
from os.path import isfile, join, splitext, exists
import re
import yaml
import sys
import pprint

def match_collection(collection, str):
    for j in collection.children:
        if re.match(str, j.text):
            return "True"
            break

def match_single(j, str, capture):
    match = re.match(str, j.text)
    if match:
        return (match.group(1) if capture else "True")

def match_single_multi(j, str, capture):
    match = re.search(str, j.text)
    if match:
        return match.groups()

def search_collection(collection, str, capture):
    for j in collection:
        match = re.search(str, j)
        if match:
            return (match.group(1) if capture else "True")

def search_single(i, str, capture):
    match = re.search(str, i.text)
    if match:
        return (match.group(1) if capture else "True")

# parse takes a filename and subdirectory and creates the corresponding yaml/sdir/filename.yml file
def parse(filename, sdir):
    p = CiscoConfParse('configurations/' + sdir + '/' + filename)   # Load in source configuration file
    interfaces = p.find_objects(r'interface')                       # Create interfaces object
    output_config = {}                                              # Create master dict for output data
    output_config['interfaces'] = []                                # Create list of interfaces

    if interfaces:
        for i in interfaces:
            interface_dict = {}

            # Insert interface name
            interface_name = search_single(i, '^interface (\S+)$', True)
            if interface_name:
                interface_dict['name'] = interface_name

            # switchport
            switchport = match_collection(i, '^ switchport.*$')
            if switchport:
                # Create switchport sub-dict
                interface_dict['switchport'] = {}

                for j in i.children:
                    # access vlan
                    access_vlan = match_single(j, '^ switchport access vlan (\S+)$', True)
                    if access_vlan:
                        interface_dict['switchport']['access_vlan'] = str(access_vlan)

                    # switchport mode
                    mode = match_single(j, '^ switchport mode (\S+)$', True)
                    if mode:
                        interface_dict['switchport']['mode'] = mode

                    # port-security
                    port_sec = match_single(j, '^ switchport port-security$', False)
                    if port_sec:
                        interface_dict['switchport']['port_security'] = 'True'

                    # switchport trunk
                    switchport_trunk = match_collection(i, '^ switchport trunk.*$')
                    if switchport_trunk:
                        interface_dict['switchport']['trunk'] = {}

                for j in i.children:
                    # native vlan
                    native_vlan = match_single(j, '^ switchport trunk native vlan (\S+)$', True)
                    if native_vlan:
                        interface_dict['switchport']['trunk']['native_vlan'] = native_vlan
                    # allowed vlan
                    allowed_vlan = match_single(j, '^ switchport trunk allowed vlan (\S+)$', True)
                    if allowed_vlan:
                        interface_dict['switchport']['trunk']['allowed_vlan'] = allowed_vlan

            # spanning-tree
            spanning_tree = match_collection(i, '^ spanning-tree.*$')
            if spanning_tree:
                # Create spanning-tree sub-dict
                if not 'spanning_tree' in interface_dict.keys():
                    interface_dict['spanning_tree'] = {}

                for j in i.children:
                    # portfast
                    portfast = match_single(j, '^ spanning-tree portfast$', False)
                    if portfast:
                        interface_dict['spanning_tree']['portfast'] = portfast
                    # guard_root
                    guard_root = match_single(j, '^ spanning-tree guard root$', False)
                    if guard_root:
                        interface_dict['spanning_tree']['guard_root'] = guard_root

            # ip
            ip = match_collection(i, '^ ip .*$')
            if ip:
                # Create ip sub-dict
                if not 'ip' in interface_dict.keys():
                    interface_dict['ip'] = {}

                for j in i.children:

                    # ip address
                    ip_address = match_single(j, '^ ip address (.*)$', True)
                    if ip_address:
                        interface_dict['ip']['address'] = ip_address
                    # ip access_group
                    access_group = match_single_multi(j, '^ ip access-group (\S+) (\S+)$', True)
                    if access_group:
                        # Create access_group sub-dict
                        interface_dict['ip']['access_group'] = {}
                        interface_dict['ip']['access_group'][access_group[0]] = access_group[1]
                    # ip dhcp snooping trust
                    dhcp_snooping_trust = match_single(j, '^ ip dhcp snooping trust$', False)
                    if dhcp_snooping_trust:
                        interface_dict['ip']['dhcp_snooping_trust'] = dhcp_snooping_trust

            # no ip
            no_ip = match_collection(i, '^ no ip .*$')
            if no_ip:
                # Create ip sub-dict
                if not 'ip' in interface_dict.keys():
                    interface_dict['ip'] = {}

                    #interface_dict['ip'] = {}

                for j in i.children:

                    # no ip address
                    no_ip = match_single(j, '^ no ip address$', False)
                    if no_ip:
                        interface_dict['ip']['ip_address_disable'] = no_ip

                    # no ip route cache
                    no_route_cache = match_single(j, '^ no ip route-cache$', False)
                    if no_route_cache:
                        interface_dict['ip']['route_cache_disable'] = no_route_cache

            # misc
            for j in i.children:

                # description
                interface_description = match_single(j, '^ description (.*)$', True)
                if interface_description:
                    interface_dict['description'] = interface_description
                # power inline police
                power_inline_police = match_single(j, '^ power inline police$', False)
                if power_inline_police:
                    interface_dict['power_inline_police'] = power_inline_police
                # cdp disable
                cdp_disable = match_single(j, '^ no cdp enable$', False)
                if cdp_disable:
                    interface_dict['cdp_disable'] = cdp_disable
                # shutdown
                shutdown = match_single(j, '^ shutdown$', False)
                if shutdown:
                    interface_dict['shutdown'] = shutdown

            # Append the completed interface dict to the interfaces list
            output_config['interfaces'].append(interface_dict)


    # IP Config Elements
    ip_config = p.find_objects(r'ip')
    if ip_config:
        # Create ip dict
        output_config['ip'] = {}
        for i in ip_config:
            # ip dhcp snooping
            dhcp_snooping = match_single(i, '^ip dhcp snooping$', False)
            if dhcp_snooping:
                output_config['ip']['dhcp_snooping'] = dhcp_snooping
            default_gateway = match_single(i, '^ip default-gateway (\S+)$', True)
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
        acl_line = search_collection(acl, '^access-list 10 permit (172.*)$', True)
        if acl_line:
            output_config['acl'] = acl_line

    # snmp-server
    snmp = p.find_blocks(r'snmp-server')
    if snmp:
        # Create snmp dict
        output_config['snmp'] = {}

        snmp_community = search_collection(snmp, '^snmp-server community (\S+)', True)
        if snmp_community:
            output_config['snmp']['community'] = snmp_community
        snmp_location = search_collection(snmp, '^snmp-server location (.*)$', True)
        if snmp_location:
            output_config['snmp']['location'] = snmp_location
        snmp_contact = search_collection(snmp, '^snmp-server contact (.*)$', True)
        if snmp_contact:
            output_config['snmp']['contact'] = snmp_contact

    # vtp
    vtp = p.find_blocks(r'vtp')
    if vtp:
        vtp_mode = search_collection(vtp, 'vtp mode (\S+)', True)
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

    # Screen output
    print
    print(sdir + '/' + filename + ' YAML Output:')
    print
    print yaml.dump(output_config, default_flow_style=False, explicit_start=True)

    # Make sure the directory we're trying to write to exists. Create it if it doesn't
    out_path = 'yaml/' + sdir + '/'
    if not exists(out_path):
        makedirs(out_path)

    # Write foo.yml to the subdir in yaml/ that corresponds to the dir where we got the input file in configurations/
    with open(out_path + splitext(filename)[0] + '.yml', 'w') as outfile:
        yaml.dump(output_config, outfile, default_flow_style=False, explicit_start=True)

root_path = 'configurations/'           # specify root directory
subdirs = walk(root_path).next()[1]     # obtain all subdirectories
subdirs.append('');                     # add root directory

for s in subdirs:
    files = [f for f in listdir(root_path + s) if isfile(join(root_path + s, f))]
    for f in files:
        if f != '.gitignore':           # let's not try to parse gitignores
            parse(f, s)
