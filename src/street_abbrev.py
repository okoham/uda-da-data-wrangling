#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
Auditing and correction of addr:street values: do they contain abbreviations?

If run as a main program, it takes the path to an OSM file as input, identifies 
tag elements containing street names, and prints out those that have abbreviations.
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re

# replace abbreviations and incorrect typing
ABBREV_MAPPING = { 
    "Str.$": "Straße",
    "str.$": "straße",
    "Strasse": "Straße",
    "strasse": "straße"
    }
ABBREV_RE = re.compile("|".join(ABBREV_MAPPING.keys()))


def is_streetname(elem):
    """Return True if the tag elment is a street name"""
    return (elem.attrib['k'] == "addr:street")


def audit_abbreviations(streets_with_abbrev, streetname):
    """Assign street name to a category, if it matches one of the criteria 
    defined in ABBREV_MAPPING"""
    m = ABBREV_RE.search(streetname)
    if m:
        streets_with_abbrev[m.group()].add(streetname)


def audit(osmpath):
    osm = open(osmpath, "r", encoding='utf-8')
    streets = defaultdict(set)
    for event, elem in ET.iterparse(osm, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_streetname(tag):
                    audit_abbreviations(streets, tag.attrib['v'])
    osm.close()
    return streets


def update_streetname(streetname):
    """Return an updated version of the street name with common abbreviations replaced."""
    for pattern, repl in ABBREV_MAPPING.items():
        streetname = re.sub(pattern, repl, streetname)
    return streetname


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Audit street names. Prints results to stdout.')
    parser.add_argument('osmpath', type=str, help='Path to OSM file')
    args = parser.parse_args()

    abbrev_types = audit(args.osmpath) # dict {str:set {str}}
    for abbrev_type, street_names in abbrev_types.items():
        print("\n%s:" % abbrev_types)
        for street_name in sorted(street_names):
            print("    %s" % street_name)                

