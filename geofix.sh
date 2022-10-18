#!/usr/bin/env bash

# Author: Dmitri Popov, dmpop@tokyoma.de

#######################################################################
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################

# Check whether the Photon service is reachable
wget -q --spider https://photon.komoot.io/
if [ $? -ne 0 ]; then
  echo "Photon is not reachable. Check your Internet connection." >>"/tmp/geofixlog" 2>&1
  exit 1
fi

gps=$(exiftool -gpslatitude "$1")
if [ -z "$gps" ]; then
  # Use the curl tool to fetch geographical data via an HTTP request using the Photon service
  # Pipe the output in the JSON format to the jq tool to extract the latitude and longitude values
  geo="$(curl -k "https://photon.komoot.io/api/?q=$location")"
  lat=$(echo "$geo" | jq '.features | .[0] | .geometry | .coordinates | .[1]')
  lon=$(echo "$geo" | jq '.features | .[0] | .geometry | .coordinates | .[0]')

  # Calculate the latitude and longitude references
  # The latitude reference is N if the latitude value is positive
  # The latitude reference is S if the latitude value is negative
  # Use the bc tool to compare the value of the $lat variable and assign the correct latitude reference
  if (($(echo "$lat > 0" | bc -l))); then
    latref="N"
  else
    latref="S"
  fi
  # Calculate the correct longitude references for the given longitude value
  # The longitude reference is E if the longitude value is positive
  # The longitude reference is W if the longitude value is negative
  if (($(echo "$lon > 0" | bc -l))); then
    lonref="E"
  else
    lonref="W"
  fi
  # Write the obtained geographical coordinates into EXIF metadata of the file
  echo $lat $lon
  exiftool -overwrite_original -GPSLatitude=$lat -GPSLatitudeRef=$latref -GPSLongitude=$lon -GPSLongitudeRef=$lonref $1
fi
