#!/bin/sh
uvicorn main:app --host 0.0.0.0 --reload --port 8000 | tee log.log 

