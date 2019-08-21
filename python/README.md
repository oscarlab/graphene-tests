# Python 2.7 example

This directory contains an example for running Python in Graphene, including
the Makefile and a template for generating the manifest. The application is
tested on Ubuntu 16.04, with both normal Linux and SGX platforms.

# Generating the manifest

## Build for Linux

Run `make` (non-debug) or `make DEBUG=1` (debug) in the directory.

## Build for SGX

Run `make SGX=1` (non-debug) or `make SGX=1 DEBUG=1` (debug) in the directory.

## Build with a local Python installation

By default, the `make` command build the manifest against the system installation.
If you have a local installation directly compiled from the source code, you
may build the manifest with the `PYTHONHOME` variable. For example:

```
make PYTHONHOME=<install path>/lib/python2.7 SGX=1
```

# Run Python with Graphene

Here's an example of running a Python script into Graphene:

Without SGX:
```
./pal_loader python.manifest scripts/helloworld.py
./pal_loader python.manifest scripts/fibonacci.py
./pal_loader python.manifest scripts/test-numpy.py
./pal_loader python.manifest scripts/test-scipy.py
```

With SGX:
```
SGX=1 ./pal_loader python.manifest scripts/helloworld.py
SGX=1 ./pal_loader python.manifest scripts/fibonacci.py
SGX=1 ./pal_loader python.manifest scripts/test-numpy.py
SGX=1 ./pal_loader python.manifest scripts/test-scipy.py
```
