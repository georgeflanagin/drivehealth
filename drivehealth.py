# -*- coding: utf-8 -*-
import typing
from   typing import *

min_py = (3, 8)

###
# Standard imports, starting with os and sys
###
import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

###
# Other standard distro imports
###
import argparse
import contextlib
import configparser
from datetime import datetime
import getpass
import string
import sqlite3
mynetid = getpass.getuser()

###
# From hpclib
###
from   dorunrun import dorunrun
import linuxutils
from   urdecorators import trap
from fileutils import read_whitespace_file
from sqlitedb import SQLiteDB
###
# imports and objects that are a part of this project
###
verbose = False

###
# Credits
###
__author__ = 'Alina Enikeeva, George Flanagin'
__copyright__ = 'Copyright 2022'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'Alina Enikeeva'
__email__ = ['alina.enikeeva@richmond.edu']
__status__ = 'in progress'
__license__ = 'MIT'

db = None

@trap
def drivehealth_main(myargs:argparse.Namespace) -> int:
    global db

    # get the list of hosts
    parser = configparser.ConfigParser()
    parser.read(myargs.input) 
    mylistofhosts = parser.get("hostnames", "hosts").split(" ")

    SQL_majorinfo = """INSERT INTO majorinfo (workstation, serial_number, device_model) VALUES (?,?,?)"""
    SQL_attributes = """INSERT INTO attribute_value (workstation, serial_number, ID, raw_value) VALUES (?,?,?,?)"""

    #commands to retrieve data from drives on workstations
    cmd_list_of_drives = "ssh -o ConnectTimeout=5 root@{} 'ls -1 /dev/sd?'" #command to get the list of drives on the machine
    cmd_info = "ssh -o ConnectTimeout=5 root@{} 'smartctl --all {}'" #command to get information on each drive
    cmd_info_attr = "ssh -o ConnectTimeout=5 root@{} 'smartctl --attributes {}'" #command to get a table for attributes only
    
    #IDs of attributes of interest
    IDs_of_interest = [1, 3, 4, 5, 7, 8, 9, 10, 11, 192, 194, 196, 197, 198, 200]
           
    for host in mylistofhosts:
        list_drives = dorunrun(cmd_list_of_drives.format(host), return_datatype = str)
        for drive in list_drives.split("\n"):
            #find out device model and serial number
            report = dorunrun(cmd_info.format(host, drive), return_datatype = str)
            
            report_all = [ _.strip() for _ in report.split('\n') ]
            major_info = { line for i, line in enumerate(report_all)
                            if line.startswith('Device Model') or line.startswith('Serial Number')}
            
            major_info = dict([x.strip().split(":") for x in major_info])
            
            if major_info: #check if major_info is not empty 
                serial_number = major_info.get("Serial Number").strip() 
                device_model = major_info.get("Device Model").strip()
            
            #insert values into the table with major info
            try:
                db.execute_SQL(SQL_majorinfo, host, serial_number, device_model)
            except sqlite3.Error:
                pass

            db.commit()

            #find out the ID and corresponding raw value
            report_attributes = dorunrun(cmd_info_attr.format(host, drive), return_datatype = str)
            tabular_info = { i:line for i, line in enumerate(report_attributes.split("\n"))
                              if len(line) and line[0].strip() in string.digits }
            #print(report_all)
            for line in tabular_info.values():
                #print(line)
                line = line.strip().split(' ')
                ID = line[0]
                raw_value = " ".join(line[len(line)-7:]).strip() 
                #db.execute_SQL(SQL_attributes, serial_number, ID, raw_value)
                if int(ID) in IDs_of_interest:
                    try:
                        print(host, serial_number, ID, raw_value)
                        db.execute_SQL(SQL_attributes, host, serial_number, ID, raw_value)
                    except sqlite3.Error as e:
                        print(e)
                    #print(major_info, ID, raw_value) 
          
        db.commit()

    return os.EX_OK


if __name__ == '__main__':
    this_dir=os.path.dirname(os.path.realpath(__file__)) 

    parser = argparse.ArgumentParser(prog="drivehealth", 
        description="What drivehealth does, drivehealth does best.")
    parser.add_argument('-i', '--input', type=str, default=os.path.realpath(f"/etc/fiscalprogs/mylistofhosts.conf"),
        help="Input file that contains list of current hosts.")
    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")
    parser.add_argument('-v', '--verbose', action='store_true',
        help="Be chatty about what is taking place")
    parser.add_argument('--db', type=str, default=os.path.realpath(f"{this_dir}/drivehealth.db"),
        help="Input database name that contains information with packages installed on current workstations.")


    myargs = parser.parse_args()
    verbose = myargs.verbose
    

    try:
        db = SQLiteDB(myargs.db)
    except:
        db = None
        print(f"Unable to open {myargs.db}")
        sys.exit(EX_CONFIG)
    
    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")

