#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
"""
Goal of this script is to explore the data a bit more and apply some corrections on it.
For e.g.
a) Typo in tag names
b) Amalgamating the Zip Codes
c) Checking the "k" value for each "<tag>" and see if they can be valid keys in MongoDB, as well as see if there are any other potential problems.

We have provided you with 3 regular expressions to check for certain patterns
in the tags. As we saw in the quiz earlier, we would like to change the data model
and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with problematic characters.
Please complete the function 'key_type'.
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        attribs = element.attrib
        if(attribs.has_key("k")):
            m= lower.match(attribs["k"])
            if m is not None:
                keys['lower']=m.end()-m.start()
            n = lower_colon.match(attribs["k"])
            if n is not None:
                keys['lower_colon']=n.end()-n.start()
            p = problemchars.match(attribs["k"])
            if p is not None:
                keys['problemschars']=p.end()-p.start()
              ##for tag in element.iter("k"):
        ##    print tag.attrib
         #   break

        # YOUR CODE HERE
        pass
        
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    element_dict={}
    for _, element in ET.iterparse(filename):
        if element_dict.has_key(elem):
            element_dict[elem]=1


        # keys = key_type(element, keys)
        


    for key in element_dict.keys:
        pprint.pprint(key)



def test():
    # You can use another testfile 'map.osm' to look at your solution
    # Note that the assertions will be incorrect then.
    keys = process_map('chicago_illinois.osm')
    pprint.pprint(keys)
    assert keys == {'lower': 5, 'lower_colon': 0, 'other': 1, 'problemchars': 1}


if __name__ == "__main__":
    test()