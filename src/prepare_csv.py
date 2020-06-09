#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIXME: some description
"""
import csv
import pprint
import re
import os.path
import xml.etree.cElementTree as ET

import cerberus
import schema

from addr_city import is_cityname, update_cityname
from street_housenum import is_streetname, update_streetname


NODES_FILE = "nodes.csv"
NODE_TAGS_FILE = "nodes_tags.csv"
WAYS_FILE = "ways.csv"
WAY_NODES_FILE = "ways_nodes.csv"
WAY_TAGS_FILE = "ways_tags.csv"

# FIXME: what about upper case?
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

DEFAULT_TAG_TYPE = "regular"


def is_unproblematic(k):
    return PROBLEMCHARS.search(k) is None
        

def has_colon(k):
    return LOWER_COLON.match(k)


def split_colon(k):
    items = k.split(":")
    if len(items) == 1:
        return DEFAULT_TAG_TYPE, k 
    elif len(items) == 2:
        return items
    else: 
        return items[0], ":".join(items[1:])


def process_tag(tag, element_id):
    k = tag.attrib["k"]
    v = tag.attrib["v"]
    if is_unproblematic(k):
        typ, key = split_colon(k)
        # apply selected cleaning functions
        if is_cityname(tag):
            v = update_cityname(v)
        if is_streetname(tag):
            v = update_streetname(v)
        d = {'id': element_id, 'key': key, 'value': v, 'type': typ}
        return d
    else:
        return None


def shape_element(element):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        # attributes
        for field in NODE_FIELDS:
            value = element.attrib[field] if field in element.attrib else ""
            node_attribs[field] = value
        nid = node_attribs["id"]
        # tags
        for tag in element.iter("tag"):
            d = process_tag(tag, nid)
            if d is not None:
                tags.append(d)
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        # attributes
        for field in WAY_FIELDS:
            value = element.attrib[field] if field in element.attrib else ""
            way_attribs[field] = value        
        wid = way_attribs['id']
        # tags
        for tag in element.iter("tag"):
            d = process_tag(tag, wid)
            if d is not None:
                tags.append(d)
        # way nodes
        position = 0
        for nd in element.iter("nd"):
            d = {"id": wid, "node_id": nd.attrib["ref"], "position": position}
            way_nodes.append(d)
            position += 1
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""
    dirname = os.path.dirname(file_in)
    with open(os.path.join(dirname, NODES_FILE), 'w', encoding="utf-8", newline='') as nodes_file, \
         open(os.path.join(dirname, NODE_TAGS_FILE), 'w', encoding="utf-8", newline='') as nodes_tags_file, \
         open(os.path.join(dirname, WAYS_FILE), 'w', encoding="utf-8", newline='') as ways_file, \
         open(os.path.join(dirname, WAY_NODES_FILE), 'w', encoding="utf-8", newline='') as way_nodes_file, \
         open(os.path.join(dirname, WAY_TAGS_FILE), 'w', encoding="utf-8", newline='') as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    OSM_PATH = "full/ruegen_20200416.osm"
    process_map(OSM_PATH, validate=False)
