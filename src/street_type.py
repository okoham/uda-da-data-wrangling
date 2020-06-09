#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
Auditing and correction of street names.

If run as a main program, it takes the path to an OSM file as input, identifies 
tag elements containing street names, groups them according to typical street types 
abd prints out the result.
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re

# typical street names
STREET_TYPE_RE = re.compile("|".join([
    "^(Am|An) ",
    "^(Zum|Zur|Zu) ",
    "(Straße)",
    "(Weg)$",
    "(Ring)$",
    "(Chaussee)$",
    "(Allee)$",
    "(Platz)",
    "(hof)$",
    "(berg)$",
]), re.IGNORECASE)


def is_streetname(elem):
    """Return True if the tag elment is a street name"""
    return (elem.attrib['k'] == "addr:street")


def audit_street_type(street_types, streetname):
    """Assign the street name to a category."""
    m = STREET_TYPE_RE.search(streetname)
    street_type = m.group().lower() if m else "__other__"
    street_types[street_type].add(streetname)


def audit(osmpath):
    osm = open(osmpath, "r", encoding='utf-8')
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_streetname(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm.close()
    return street_types


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Audit street names. Prints results to stdout.')
    parser.add_argument('osmpath', type=str, help='Path to OSM file')
    args = parser.parse_args()

    street_types = audit(args.osmpath) # dict {str:set {str}}
    for street_type, street_names in street_types.items():
        print("\n%s:" % street_type)
        for street_name in sorted(street_names):
            print("    %s" % street_name)
