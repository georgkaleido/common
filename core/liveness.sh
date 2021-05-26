#!/bin/bash

export PNOW=$(date +%s)
export PSTART=$(stat -c '%Y' currently_processing 2> /dev/null || echo 9999999999)
export PTHRESHOLD=$(($PNOW-15))

if [ "$PSTART" -eq "9999999999" ]; then
  echo "$PNOW: Not processing currently. HC OK."
  exit 0;
fi

if [ "$PSTART" -lt "$PTHRESHOLD" ]; then
  echo "$PNOW: Currently processing since $PSTART. HC failed."
  exit 1;
fi

echo "$PNOW: Currently processing since $PSTART. HC OK."

exit 0;
