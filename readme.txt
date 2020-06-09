--------------
Provided files
--------------

Documentation
-------------
doc.pdf - the report
readme.txt - this file
links.txt - visited links


Data 
----
# a 6 MB sample of the full OSM file
ruegen_20200416_sample.osm

Code
----

# script for creating a smaller sample of the full dataset
sampling.py

# scripts for auditing and cleaning various aspects of the data
count_elments.py
tags.py
street_abbrev.py
street_housenum.py
street_type.py
postcode.py
addr_city.py

# scripts for extracting, cleaning and transforming into csv
# use of some of the cleaning functions above
prepare_csv.py
schema.py

# files for creating and filling the database 
load_database.py
osm.sql

# jupyter notebook for queries (printed version in appendix) 
queries.ipynb
