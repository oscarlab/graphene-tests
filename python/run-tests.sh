#!/bin/sh

set -e

echo -e "\n\nRunning helloworld.py:"
./pal_loader python.manifest scripts/helloworld.py > OUTPUT
grep -q "Hello World" OUTPUT && echo "[ SUCCESS ]"
rm OUTPUT

echo -e "\n\nRunning fibonacci.py:"
./pal_loader python.manifest scripts/fibonacci.py > OUTPUT
grep -q "fib2              55" OUTPUT && echo "[ SUCCESS ]"
rm OUTPUT

echo -e "\n\nRunning test-numpy.py:"
./pal_loader python.manifest scripts/test-numpy.py > OUTPUT
grep -q "dot: " OUTPUT && echo "[ SUCCESS ]"
rm OUTPUT

echo -e "\n\nRunning test-scipy.py:"
./pal_loader python.manifest scripts/test-scipy.py > OUTPUT
grep -q "cholesky: " OUTPUT && echo "[ SUCCESS ]"
rm OUTPUT

./web-test.sh
