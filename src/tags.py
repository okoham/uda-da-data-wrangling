#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Investigation of <tag> elements.

If run as a main program, it takes the path to an OSM file as input, categorizes
and counts the keys on <tag> elements, and prints the result to stdout.
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re

KEY_CATEGORIES = ['lower', 'lower_colon', 'problemchar', 'other']

RE_LOWER = re.compile(r'^([a-z_]+)$') # simple keys like "building", all lowercase
RE_LOWER_COLON = re.compile(r'^(([a-z_]+):)+([a-z_]+)$') # complex keys like "seamark:light:orientation"
RE_PROBLEMCHAR = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]') # keys that contain problematic characters


def key_category(key):
    """Return category of a key (string)."""
    if RE_LOWER.match(key):
        return "lower" 
    elif RE_LOWER_COLON.match(key):
        return "lower_colon" 
    elif RE_PROBLEMCHAR.search(key):
        return "problemchar"
    else:
        return "other"


def is_tag_acceptable(element):
    """Return True if key of tag element is acceptable. 
    All keys that do not contain problematic characters are considered acceptable."""
    key = element.attrib['k']
    return key_category(key) != "problemchar"


def count(element, key_counts):
    if element.tag == "tag":
        key = element.attrib["k"]
        cat = key_category(key)
        key_counts[cat][key] += 1


def process_map(filename):
    keys = {cat: defaultdict(int) for cat in KEY_CATEGORIES}
    for event, element in ET.iterparse(filename):
        count(element, keys)
    return keys


if __name__ == "__main__":
    import argparse
    from operator import itemgetter

    parser = argparse.ArgumentParser(description='Audit <tag> elements and print results to stdout.')
    parser.add_argument('osmpath', type=str, help='Path to OSM file')
    args = parser.parse_args()

    keys = process_map(args.osmpath)

    for cat in KEY_CATEGORIES:
        print("\n*** %s ***\n" % cat)
        for key, count in sorted(keys[cat].items(), key=itemgetter(1), reverse=True):
            print("%s %i" % (key, count))
