# Apache example

This directory contains an example for running Apache (version 2.4.41)
in Graphene, including the Makefile and a template for generating the manifest.
The application is tested on Ubuntu 16.04, with both normal Linux and SGX
platforms.

# Installing from the Apache source code

In this example, we build Apache from the source code instead use an existing
installation. To build Apache on Ubuntu 16.04, please make sure that the
following packages are properly installed:

    sudo apt-get install -y build-essential libapr1-dev libaprutil1-dev libpcre2-dev apache2-utils

After installing the packages, run `make` (non-debug) or `make DEBUG=1` (debug)
in the directory to build and install Apache.

# Generating the manifest

## Building for Linux

Run `make` (non-debug) or `make DEBUG=1` (debug) in the directory (as the last
step of compilation/installation).

## Building for SGX

Run `make SGX=1` (non-debug) or `make SGX=1 DEBUG=1` (debug) in the directory.

# Running Apache natively, under Graphene, and under Graphene-SGX

## Running Apache natively

First, start the Apache server. By default, the installed Apached server will
use the Prefork multi-processing module (MPM).

    make start-native-server

If you wish to run Apache with the Worker MPM, run the following command
instead:

    make start-native-multithreaded-server

Because these commands will start the Apache server in the foreground, you will
need to open another console to run the client end.

Once the server has started, you can test the server with `wget`

    wget http://127.0.0.1:8001/random/10K.1.html

You may also run the benchmark using `ab` from `ApacheUtil`:

    ./benchmark-http.sh 127.0.0.1:8001

Once you have finished testing or benchmarking the Apache server, use Ctrl-C to
terminate the server.

## Running Apache in Graphene

First, start the Apache server. By default, the installed Apached server will
use the Prefork multi-processing module (MPM).

    make start-graphene-server

If you wish to run Apache with the Worker MPM, run the following command
instead:

    make start-graphene-multithreaded-server

Because these commands will start the Apache server in the foreground, you will
need to open another console to run the client end.

Once the server has started, you can test the server with `wget`

    wget http://127.0.0.1:8001/random/10K.1.html

You may also run the benchmark using `ab` from `ApacheUtil`:

    ./benchmark-http.sh 127.0.0.1:8001

Once you have finished testing or benchmarking the Apache server, use Ctrl-C to
terminate the server.

## Running Apache in Graphene-SGX

First, make sure to create the SGX-specific manifest, the signature, and the
token file. Use the following command to generate them:

    make SGX=1

Then, start the Apache server. By default, the installed Apached server will
use the Prefork multi-processing module (MPM).

    make start-graphene-server SGX=1

If you wish to run Apache with the Worker MPM, run the following command
instead:

    make start-graphene-multithreaded-server SGX=1

Because these commands will start the Apache server in the foreground, you will
need to open another console to run the client end.

Once the server has started, you can test the server with `wget`

    wget http://127.0.0.1:8001/random/10K.1.html

You may also run the benchmark using `ab` from `ApacheUtil`:

    ./benchmark-http.sh 127.0.0.1:8001

Once you have finished testing or benchmarking the Apache server, use Ctrl-C to
terminate the server.

# Clean up the directory

There are two commands for cleaning up the directory:

* `make clean`: Clean up manifest, signature, and token files.
* `make distclean`: Clean up the source code and the installation directory.
