#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict


def count_tags(filename):
    tag_counts = defaultdict(int)
    for event, elem in ET.iterparse(filename, events=('end',)):
        tag_counts[elem.tag] += 1
    return tag_counts
        

if __name__ == "__main__":
    #filename = "sample.osm"
    filename = "full/ruegen_20200416.osm"
    tags = count_tags(filename)
    pprint.pprint(dict(tags))
