#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
"""

-----------Goal of this script--------------
a) Prepare the data model as described by specification below. This is the main file to convert xml to data mode specially the below method shape_element
b) Learn to parse large xml files in python

Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

#OSMFILE = "chicago_illinois.osm"
OSMFILE = "seattle_washington.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Rd.": "Road",
            "Ave": "Avenue",
            "Blvd":"Boulevard",
            "Blvd.":"Boulevard",
            "Ct":"Court",
            "Rd":"Road",
            "Ct.":"Court",
            "Pky":"Parkway",
            "Rd.":"Road",
            "Pky.":"Parkway"
            }


def audit_street_type( street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            return update_name(street_name,mapping)
        else:
            return street_name
            


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])    
    return street_types


def update_name(name, mapping):
    
    for key in mapping.keys():
        index = name.find(key)
        lenOfIndex = len(name)-index
        if name.find(key)>-1 and len(key) == lenOfIndex:
            name=name.replace(key,mapping[key])

    return name


# This function is the crux of data model we are going to create.
# It checks the element to meet the below specification
# Identifies if it has any problematic characters as defined by regexp
#- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
#    - attributes in the CREATED array should be added under a key "created"
#    - attributes for latitude and longitude should be added to a "pos" array,
#      for use in geospacial indexing. Make sure the values inside "pos" array are floats
#      and not strings. 
#- if second level tag "k" value contains problematic characters, it should be ignored
#- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
#- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
#  same as any other tag.
#- if there is a second ":" that separates the type/direction of a street,
#  the tag should be ignored, for example:
##

def shape_element(element):
    node = {}
    address={}
    pos=[]
    created={}
    
    if element.tag == "node" or element.tag == "way" :
        attribs =element.attrib
        for key in attribs.keys():            
            if key=='lat' or key=='lon':                
                pos.append(float(attribs[key]))
            elif key in CREATED:
                created[key]=attribs[key]            
            else:
                node[key]=attribs[key]
        for elem in element.iter("tag"):
                attribs = elem.attrib
                if(attribs.has_key("k")): 
                    #print "got k"                                     
                    p = problemchars.match(attribs["k"])
                    if p is not None:
                        print p.group()
                        continue                    
                    l = lower.match(attribs["k"])
                    if l is not None:
                        node[attribs["k"]]=attribs["v"]
                        #print "lower==>"+ l.group()
                    lc = lower_colon.match(attribs["k"])
                    if lc is not None:
                         if lc.group()=="addr:street":
                             address['street']=audit_street_type(attribs["v"])                                 
                         elif lc.group()[:lc.group().index(":")] == "addr":
                             keyname = lc.group()[lc.group().index(":")+1:]
                             val =attribs["v"]
                             address[keyname]=val
                        #print keyname+" ==> "+ val
                elem.clear()
         

        # YOUR CODE HERE
        node["pos"]=pos
        node["created"]=created
        node["address"]=address
        node["type"]=element.tag
         
        element.clear()   # This clear is cruicial to make large files(order of 1 GB) parse
        return node
    else:        
        return None



def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    
    with codecs.open(file_out, "w") as fo:
        for evt, element in ET.iterparse(file_in):            
            el = shape_element(element)            
            if el is not None:                               
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n") 
               
            #else:
                #element.clear()
                 
    

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
  
    process_map('seattle_washington.osm')
    #pprint.pprint(data)
    
    #correct_first_elem = {
    #    "id": "261114295", 
    #    "visible": "true", 
    #    "type": "node", 
    #    "pos": [41.9730791, -87.6866303], 
    #    "created": {
    #        "changeset": "11129782", 
    #        "user": "bbmiller", 
    #        "version": "7", 
    #        "uid": "451048", 
    #        "timestamp": "2012-03-28T18:31:23Z"
    #    }
    #}
    #assert data[0] == correct_first_elem
    #assert data[-1]["address"] == {
    #                                "street": "West Lexington St.", 
    #                                "housenumber": "1412"
    #                                  }
    #assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
    #                                "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()