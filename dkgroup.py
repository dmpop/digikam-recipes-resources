#!/usr/bin/env python3
# -*- coding: utf8 -*-
#####
#    Copyright (C) 2015  J. Sabater
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
######
"""
Command line interface to group raw and normal files in a Digikam album.
systems.
"""

from __future__ import print_function, unicode_literals
import sqlite3
import getpass
import argparse
import os.path

user = getpass.getuser()
dk_database = "/home/{}/Pictures/digikam4.db".format(user)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CWD = os.getcwd()
raw_exts = [".ARW", ".NEF", ".arw", ".nef"]
jpg_exts = ["JPG", "jpg", "jpeg"]


if __name__ == "__main__":
    # Parse the command line options
    parser = argparse.ArgumentParser(description='Group RAW files and JPEG photos in a digiKam album')
    parser.add_argument('-r','--recursive', action="store_true", default=False, 
                        help='Check also the subdirectories')
    parser.add_argument('-n','--dry-run', action="store_true", default=False, 
                        help='')
    parser.add_argument('-d','--db', 
                        help='Path to the digiKam SQLite database')
    parser.add_argument('album', help='Target album')
    args = parser.parse_args()
    
    
    # TODO: Check that digikam is not open
    
    # Connect to the database
    if args.db:
        conn = sqlite3.connect(args.db)
    else:
        try:
            conn = sqlite3.connect(dk_database)
        except:
            print("Failed to open digiKam database")
    c = conn.cursor()
    
    # Get the correct path to the album_path
    # TODO: Improve the detection of the album name
    try:
        d = unicode(args.album, encoding='utf-8')
    except(NameError):
        d = args.album
    
    album_path = d
    if not album_path.startswith(u"/"):
        album_path = u"/"+album_path
    if album_path.endswith(u"/"):
        album_path = album_path[:-1]
    print(album_path)
    
    # Get the album name
    try:
        c.execute("SELECT * FROM Albums WHERE relativePath = '%s'" % album_path)
    except:
        print("Specified album was found.")
    #if c.rowcount != 1:
    #    raise ValueError("{} albums with this path were found".format(c.rowcount))
    
    album = c.fetchone()
    print("Album name: {}".format(album))
    
    # Get the images of the album
    c.execute("SELECT id, name FROM Images WHERE album = '%s'" % album[0])
    data = [list(row) for row in c.fetchall()]
    zdata = list(zip(*data))
    
    # Get the images and check if they are raw images and if there is any
    #  jpeg image with the same name
    for row in data:
        name, ext = os.path.splitext(os.path.basename(row[1]))
        ext_check = ext[1:].lower()
        raw_names = [name+e for e in raw_exts]
        
        if ext_check in jpg_exts:  # Check only RAW corresponding to JPEG images
            i = -1
            for raw_name in raw_names:  # Get the corresponding RAW name
                if raw_name in zdata[1]:
                    i = zdata[1].index(raw_name)
                    break
            if i == -1:
                continue
                    
            print(name, row[0], zdata[0][i])
            # Check if they are already linked
            c.execute("SELECT * FROM ImageRelations "
                "WHERE (subject = ? AND object = ?) "
                "OR (subject = ? AND object = ?)", 
                (row[0], zdata[0][i], zdata[0][i], row[0]))
            imrel = c.fetchall()
            #print(len(imrel), imrel)
            if len(imrel) > 0:
                print("Already grouped items (count: {})".format(len(imrel)))
                continue
            if not args.dry_run:
                #print("execute")
                c.execute("INSERT INTO ImageRelations values (?, ?, 2)", (row[0], zdata[0][i]))
        
    conn.commit()
    conn.close()
