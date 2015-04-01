#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
"""
-------Goal of Script:
a) Identify unique users for a given example file
b) learn to use element.attrib

========================================= INSTRUCTIONS FROM CLASS VIDEO ===============================================
Your task is to explore the data a bit more.
The first task is a fun one - find out how many unique users
have contributed to the map in this particular area!

The function process_map should return a set of unique user IDs ("uid")
"""

def get_user(element):
    return


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.tag=="node":
            attribs = element.attrib
            if attribs.has_key("user"):
                users.add(attribs["user"])        

    return users


def test():
    users = process_map('example.osm')
    pprint.pprint(users)
    assert len(users) == 6



if __name__ == "__main__":
    test()