#!/usr/bin/env bash

## We really need to pick a unique ephemeral port; start by just picking pid+1024
PORT=$(($$ + 1024))

echo "\n\nRun a HTTP server in the background on port " + $PORT
python3 scripts/dummy-web-server.py $PORT & echo $! > server.PID
sleep 1
echo "\n\nRun test-http.py:"
./pal_loader python.manifest scripts/test-http.py 127.0.0.1 $PORT > OUTPUT1
wget -q http://127.0.0.1:$PORT/ -O OUTPUT2
diff -q OUTPUT1 OUTPUT2 || exit $?
kill `cat server.PID`
rm -f OUTPUT1 OUTPUT2 server.PID
