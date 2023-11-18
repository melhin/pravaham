#!/bin/bash

i=0;
while [ $i -lt $2 ] ;do
    log="/tmp/sse_log_`date +%s`"
    echo "Sending request to $1 worker $i saving log file to $log"
    curl -i -N $1 -s -o $log &
    i=`expr $i + 1`;
done
