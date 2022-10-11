#!/usr/bin/env bash

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

cd "$2"
fcount=$(ls -1 | wc -l)
# Check for GPX files and GPSBabel
if [ "$fcount" -eq "0" ]; then
    echo "No GPX files found." >>"/tmp/geocorrelate-on-import.log"
    exit 1
fi
# Geocorrelate with a single GPX file
if [ "$fcount" -eq "1" ]; then
    track=$(ls "$2")
    exiftool -q -q -m -overwrite_original -geotag "$track" -geosync=180 "$1" >>"/tmp/geocorrelate-on-import.log" 2>&1
elif [ "$fcount" -gt "1" ]; then
    ff=""
    for f in *.gpx; do
        ff="$ff -f $f"
    done
    gpsbabel -i gpx $ff -o gpx -F "/tmp/merged-track.gpx"
    track="/tmp/merged-track.gpx"
    exiftool -q -q -m -overwrite_original -geotag "$track" -geosync=180 "$1" >>"/tmp/geocorrelate-on-import.log" 2>&1
else
    echo "Something went wrong. Geotagging skipped." >>"/tmp/geocorrelate-on-import.log"
fi
