# Lighttpd example

This directory contains an example for running Lighttpd (version 1.4.54)
in Graphene, including the Makefile and a template for generating the manifest.
The application is tested on Ubuntu 16.04, with both normal Linux and SGX
platforms.

# Installing from the Lighttpd source code

In this example, we build Lighttpd from the source code instead of using an existing
installation. To build Lighttpd on Ubuntu 16.04, please make sure that the
following packages are installed:

    sudo apt-get install -y build-essential apache2-utils

## Linux

Run `make` (non-debug) or `make DEBUG=1` (debug) in the directory.

## SGX

Run `make SGX=1` (non-debug) or `make SGX=1 DEBUG=1` (debug) in the directory to prepare Lighttpd to run on SGX.

# Running Lighttpd natively, under Graphene, and under Graphene-SGX

First, start the Lighttpd server. By default, the installed Lighttpd server will use the Prefork
multi-processing module (MPM). Execute one of the following commands to start lighttpd either natively
(non-Graphene), on Graphene or Graphene-SGX, respectively.

    make start-native-server
    make start-graphene-server
    SGX=1 make start-graphene-server

If you wish to run Lighttpd with the Worker MPM (multi-threaded instead of multi-process), run one of the
following commands instead. Again, either run Lighttpd natively, with Graphene or Graphene-SGX.

    make start-native-multithreaded-server
    make start-graphene-multithreaded-server
    SGX=1 make start-graphene-multithreaded-server

Because these commands will start the Lighttpd server in the foreground, you will
need to open another console to run the client.

Once the server has started, you can test it with `wget`

    wget http://127.0.0.1:8001/random/10K.1.html

You may also run the benchmark script using `ab` (Apachebench)

    ./benchmark-http.sh 127.0.0.1:8001

Once you have finished testing or benchmarking the Lighttpd server, use Ctrl-C to
terminate the server.

# Clean up the directory

There are two commands for cleaning up the directory:

* `make clean`: Clean up manifest, signature, and token files.
* `make distclean`: Clean up the source code and the installation directory.
