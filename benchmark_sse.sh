#!/bin/bash

i=0;
while [ $i -lt 50 ] ;do
    #curl -i -N http://localhost:8002/realtime/content/ -s -o /dev/null &
    echo "log will be stored here /tmp/log_$i"
    curl -i -N http://localhost:8002/realtime/content/ -s -o /tmp/log_$i &
    i=`expr $i + 1`;
done

