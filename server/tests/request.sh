#!/bin/sh
action="$1"
if [ $action = "start" ]
then
    curl -X 'POST' http://127.0.0.1:8000/ai/Start/ -H 'Content-Type: application/json' -d  @start.json
elif [ $action = "end" ] 
then
    curl -X 'POST' http://127.0.0.1:8000/ai/END/ -H 'Content-Type: application/json' -d  @end.json
elif [ $action = "setting" ]
then
    curl -X 'POST' http://127.0.0.1:8000/ai/Setting/ -H 'Content-Type: application/json' -d  @setting.json
else
    curl -X 'POST' http://127.0.0.1:8000/ai/Setting/ -H 'Content-Type: application/json' -d  @empty.json
fi