import sqlite3
import csv
import os.path
import argparse

# table names, and csv file names
TABLES = ["nodes", "nodes_tags", "ways", "ways_tags", "ways_nodes"]
SCHEMA = "osm.sql"

def insert_template(tablename, fieldnames):
    """Return an SQL INSERT query template for table tablename with field names fieldnames."""
    return "insert into {} ({}) values ({});".format(tablename,
                                                     ", ".join(fieldnames),
                                                     ", ".join([":"+field for field in fieldnames]))


parser = argparse.ArgumentParser(description='Create database and fill with preprocessed csv files.')
parser.add_argument('directory', type=str, help='directory where csv files reside')
parser.add_argument('dbfile', type=str, help='name of database file')
args = parser.parse_args()

# create database
conn = sqlite3.connect(os.path.join(args.directory, args.dbfile))
cur = conn.cursor()

# read the SQL for table definition
with open(SCHEMA, encoding="utf-8") as fp:
    sql_schema = fp.read()    
cur.executescript(sql_schema)

for table in TABLES:
    print("reading %s ...  "%table, end='')
    csv_path = os.path.join(args.directory, table+".csv")
    with open(csv_path, encoding='utf-8') as fp:
        reader = csv.DictReader(fp)
        template = insert_template(table, reader.fieldnames)
        # insert data
        for row in reader:
            cur.execute(template, row)
    # info - how many entries were inserted?
    cur.execute("select count(*) from %s;"%table)
    print("%i entries" % cur.fetchone()[0])

# done
conn.commit()
conn.close()