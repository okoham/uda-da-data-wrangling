#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
Auditing and correction of addr:city values: do they contain extra describing words?

If run as a main program, it takes the path to an OSM file as input, identifies 
tag elements containing city names, and prints out those that additions.
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re

RE_CITY_WITH_ADDON = re.compile("^Ostseebad|^Insel|[^ a-zäöüßA-ZÄÖÜ-]")


def is_cityname(elem):
    """Return True if the tag elment is a city name"""
    return (elem.attrib['k'] == "addr:city")


def audit_cityname(funny, cityname):
    """Return citynames containing special characters"""
    m = RE_CITY_WITH_ADDON.search(cityname)
    if m:
        funny[cityname] += 1


def audit(osmpath):
    osm = open(osmpath, "r", encoding='utf-8')
    cities = defaultdict(int)
    for event, elem in ET.iterparse(osm, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_cityname(tag):
                    audit_cityname(cities, tag.attrib['v'])
    osm.close()
    return cities


def update_cityname(cityname):
    """Update the tag value with cleaned city name: 
    - slash, spaces before, everything behind removed.
    - leading 'Ostseebad' or 'Insel' plus space removed"""
    return re.sub("^Ostseebad *|^Insel *| */.*$", "", cityname)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Audit addr:city names. Prints funny results to stdout.')
    parser.add_argument('osmpath', type=str, help='Path to OSM file')
    args = parser.parse_args()

    cities = audit(args.osmpath) # dict {str: int}
    for city, count in cities.items():
        print(city, count)

