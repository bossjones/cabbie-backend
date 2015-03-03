#!/bin/sh

# for crontab
# -----------

# make temp folder
DRIVER_LOCATION_TEMP=$HOME/driver_location
mkdir -p $DRIVER_LOCATION_TEMP/output

# copy last 1000 lines
tail -n 1000 $HOME/logs/cabbie/cabbie-location.log.stderr > $DRIVER_LOCATION_TEMP/cabbie-location.log.tmp

# parse geolocations
awk -f $HOME/workspace/cabbie-backend/driver_location/extract.awk $DRIVER_LOCATION_TEMP/cabbie-location.log.tmp > $DRIVER_LOCATION_TEMP/output/driver_location.txt 
