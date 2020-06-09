#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
Auditing and correction of addr:street values: do they contain trailing housenumbers?

If run as a main program, it takes the path to an OSM file as input, identifies 
tag elements containing street names, and prints out those that have trailing numbers.
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re


# detect and remove trailing house numbers: latin numbers and roman literals. 
# Latin numbers: using I, V and X only. Could be extended if necessary.
HOUSENUM_RE = re.compile("\s+(\d+|[IVX]+)\s*$")


def is_streetname(elem):
    """Return True if the tag elment is a street name"""
    return (elem.attrib['k'] == "addr:street")


def audit_housenum(streets_with_housenum, streetname):
    """Add street name to set if it has trailing numbers"""
    m = HOUSENUM_RE.search(streetname)
    if m:
        streets_with_housenum.add(streetname)

def audit(osmpath):
    osm = open(osmpath, "r", encoding='utf-8')
    streets = set([])
    for event, elem in ET.iterparse(osm, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_streetname(tag):
                    audit_housenum(streets, tag.attrib['v'])
    osm.close()
    return streets


def update_streetname(streetname):
    """Return an updated version of the street name with trailing numbers removed"""
    return re.sub(HOUSENUM_RE, '', streetname)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Audit street names. Prints results to stdout.')
    parser.add_argument('osmpath', type=str, help='Path to OSM file')
    args = parser.parse_args()

    for streetname in audit(args.osmpath): # set {str}
        print(streetname)  