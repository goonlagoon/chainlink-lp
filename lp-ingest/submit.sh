#!/bin/bash
echo "Wait for namenode to exit safe mode"
sleep 10

echo "Running ingest script"
python  /app/src/ingest.py