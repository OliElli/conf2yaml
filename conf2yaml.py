#!/usr/bin/env python
from ciscoconfparse import CiscoConfParse
from pprint import pprint
import re

config = 'configurations/tests1.svn'

p = CiscoConfParse(config)

ints = p.find_objects(r"interface")

print "  interfaces:"
for i in ints:
    match = re.search('^interface (\S+)$',i.text)
    print "  - name", match.group(1)
    for j in i.children:
        match = re.match('^ switchport access vlan (\S+)$',j.text)
        if match:
            print "    access_vlan:", match.group(1)
        match = re.match('^ switchport mode (\S+)$',j.text)
        if match:
            print "    mode:", match.group(1)
