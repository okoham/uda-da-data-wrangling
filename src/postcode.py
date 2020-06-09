"""
Auditing and correction of postal code tags: do they contain trailing housenumbers?

If run as a main program, it takes the path to an OSM file as input, identifies 
tag elements containing postal codes, and prints out those that are incorrect for the 
Rügen region.

__boundary:postal_code__
- see addr:postcode

__addr:postcode__
- The tag addr:postcode=* should be used in the context of addresses for buildings and nodes.
- The postal code of the building/area. Some mappers prefer to use boundary=postal_code

__postal_code__
- You can tag ways and areas with postal_code=* to describe the postal code of an area or a street.

__openGeoDB:postal_codes__

__object:postcode__ 
- Tagging of the numeric postcode of the area the POI is located in.

"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re


POCO_KEYS = ["addr:postcode", "postal_code", "openGeoDB:postal_codes", 
             "object:postcode", "boundary:postal_code"]

# https://www.plz-suche.org/de/plz-karte/postleitzahlengebiet-18
POCO_RE = re.compile(r'^18[456]\d{2}$', re.IGNORECASE)


def audit_poco(poco_types, key, poco):
    if not POCO_RE.match(poco):
        poco_types[key].add(plz)


def is_poco(elem):
    return (elem.attrib['k'] in POCO_KEYS)


def audit(osmpath):
    osm = open(osmpath, "r", encoding="utf-8")
    incorrect_postcodes = defaultdict(set)
    for event, elem in ET.iterparse(osm, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_poco(tag):
                    audit_poco(incorrect_postcodes, tag.attrib['k'], tag.attrib['v'])
    osm.close()
    return incorrect_postcodes


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Identify and list incorrect postal codes')
    parser.add_argument('osmpath', type=str, help='Path to OSM file')
    args = parser.parse_args()

    incorrect_postcodes = audit(args.osmpath)

    for key in incorrect_postcodes:
        n = len(incorrect_postcodes[key])
        print("\n%s: %i not ok"%n)
        if n > 0:
            print("  ", sorted(incorrect_postcodes[key]))
