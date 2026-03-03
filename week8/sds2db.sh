#!/bin/bash

# Usage:
# ./sds2db.sh <SDS_ROOT> <DBNAME> [NET] [STA] [CHA] [YEAR] [JDAY]

SDS_ROOT=$1
DBNAME=$2
NET=${3:-"*"}
STA=${4:-"*"}
CHA=${5:-"*"}
YEAR=${6:-"*"}
JDAY=${7:-"*"}

if [ -z "$SDS_ROOT" ] || [ -z "$DBNAME" ]; then
    echo "Usage:"
    echo "  $0 <SDS_ROOT> <DBNAME> [NET] [STA] [CHA] [YEAR] [JDAY]"
    echo
    echo "Example:"
    echo "  $0 /data/SDS redoubt AV RDT EHZ 2009 079"
    exit 1
fi

echo "SDS root:   $SDS_ROOT"
echo "Database:   $DBNAME"
echo "Network:    $NET"
echo "Station:    $STA"
echo "Channel:    $CHA"
echo "Year:       $YEAR"
echo "Julian day: $JDAY"
echo

COUNT=0

# Traverse SDS structure
find "$SDS_ROOT/$YEAR/$NET/$STA" -type f 2>/dev/null | while read file; do

    fname=$(basename "$file")

    # SDS filename pattern:
    # NET.STA.LOC.CHA.D.YEAR.JDAY
    IFS='.' read -r fnet fsta floc fcha ftype fyear fjday <<< "$fname"

    if [[ "$fcha" == $CHA && "$fyear" == $YEAR || "$YEAR" == "*" ]] && \
       [[ "$fjday" == $JDAY || "$JDAY" == "*" ]]; then

        echo "Processing $file"
        miniseed2db "$file" "$DBNAME"
        COUNT=$((COUNT+1))
    fi

done

echo
echo "Finished."