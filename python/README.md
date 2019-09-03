# Python example

This directory contains an example for running Python 2.7 in Graphene, including
the Makefile and a template for generating the manifest. The application is
tested on Ubuntu 16.04, with both normal Linux and SGX platforms. Python 3 is not
yet tested in Graphene.

# Generating the manifest

## Installing prerequisites

For generating the manifest and running the test scripts, please run the following
command to install the required Python packages:

    sudo apt-get install -f python-numpy python-scipy

## Building for Linux

Run `make` (non-debug) or `make DEBUG=1` (debug) in the directory.

## Building for SGX

Run `make SGX=1` (non-debug) or `make SGX=1 DEBUG=1` (debug) in the directory.

## Building with a local Python installation

By default, the `make` command creates the manifest for the Python binary from
the system installation. If you have a local installation, you may create the
manifest with the `PYTHONHOME` variable set accordingly. For example:

```
make PYTHONHOME=<install path>/lib/python2.7 SGX=1
```

# Run Python with Graphene

Here's an example of running Python scripts under Graphene:

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
