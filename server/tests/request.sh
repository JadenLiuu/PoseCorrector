#!/bin/sh
action="$1"
if [ $action = "ai" ]
then
    curl -X 'POST' http://192.168.112.110/_API/AiDataToDB -H 'Content-Type: application/json' -d  @ai_v2.json
elif [ $action = "start" ]
then
    curl -X 'POST' http://127.0.0.1:8000/ai/Start/ -H 'Content-Type: application/json' -d  @start.json
elif [ $action = "end" ] 
then
    curl -X 'POST' http://127.0.0.1:8000/ai/END/ -H 'Content-Type: application/json' -d  @end.json
elif [ $action = "set" ]
then
    curl -X 'POST' http://127.0.0.1:8000/ai/Setting/ -H 'Content-Type: application/json' -d  @setting.json
else
    curl -X 'POST' http://127.0.0.1:8000/ai/Setting/ -H 'Content-Type: application/json' -d  @empty.json
fi