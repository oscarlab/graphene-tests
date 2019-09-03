# lighttpd example

This directory contains an example for running lighttpd (version 1.4.54)
in Graphene, including the Makefile and a template for generating the manifest.
The application is tested on Ubuntu 16.04, with both normal Linux and SGX
platforms.

# Installing from the lighttpd source code

In this example, we build lighttpd from the source code instead of using an
existing installation. To build lighttpd on Ubuntu 16.04, please make sure that
the following packages are properly installed:

    sudo apt-get install -y build-essential apache2-utils

# Generating the manifest

## Building for Linux

Run `make` (non-debug) or `make DEBUG=1` (debug) in the directory (as the last
step of compilation/installation).

## Building for SGX

Run `make SGX=1` (non-debug) or `make SGX=1 DEBUG=1` (debug) in the directory.

# Running lighttpd natively, under Graphene, and under Graphene-SGX

## Running lighttpd natively

First, start the lighttpd server with the following command:

    make start-native-server

If you wish to run lighttpd with multi-threading, run the following command:

    make start-native-multithreaded-server

Because these commands will start the lighttpd server in the foreground, you will
need to open another console to run the client end.

Once the server has started, you can test the server with `wget`

    wget http://127.0.0.1:8001/random/10K.1.html

You may also run the benchmark using `ab` from `apache2-utils`:

    ./benchmark-http.sh 127.0.0.1:8001

If you wish to run lighttpd with SSL (i.e., as HTTPS server), run the following
command:

    make start-native-ssl-server

Then, you can test the client end with SSL using `wget`:

    wget --no-check-certificate https://127.0.0.1:8001/random/10K.1.html

Once you have finished testing or benchmarking the lighttpd server, use Ctrl-C to
terminate the server.

## Running lighttpd in Graphene

First, start the lighttpd server with the following command:

    make start-graphene-server

If you wish to run lighttpd with multi-threading, run the following command:

    make start-graphene-multithreaded-server

Because these commands will start the lighttpd server in the foreground, you will
need to open another console to run the client end.

Once the server has started, you can test the server with `wget`

    wget http://127.0.0.1:8001/random/10K.1.html

You may also run the benchmark using `ab` from `apache2-utils`:

    ./benchmark-http.sh 127.0.0.1:8001

If you wish to run lighttpd with SSL (i.e., as HTTPS server), run the following
command:

    make start-graphene-ssl-server

Then, you can test the client end with SSL using `wget`:

    wget --no-check-certificate https://127.0.0.1:8001/random/10K.1.html

Once you have finished testing or benchmarking the lighttpd server, use Ctrl-C to
terminate the server.

## Running lighttpd in Graphene-SGX

First, make sure to create the SGX-specific manifest, the signature, and the
token file. Use the following command to generate them:

    make SGX=1

Then, start the lighttpd server with the following command:

    make start-graphene-server SGX=1

If you wish to run lighttpd with multi-threading, run the following command
instead:

    make start-graphene-multithreaded-server SGX=1

Because these commands will start the lighttpd server in the foreground, you will
need to open another console to run the client end.

Once the server has started, you can test the server with `wget`

    wget http://127.0.0.1:8001/random/10K.1.html

You may also run the benchmark using `ab` from `apache2-util`:

    ./benchmark-http.sh 127.0.0.1:8001

If you wish to run lighttpd with SSL (i.e., as HTTPS server), run the following
command:

    make start-graphene-ssl-server SGX=1

Then, you can test the client end with SSL using `wget`:

    wget --no-check-certificate https://127.0.0.1:8001/random/10K.1.html

Once you have finished testing or benchmarking the lighttpd server, use Ctrl-C to
terminate the server.

# Clean up the directory

There are two commands for cleaning up the directory:

* `make clean`: Clean up manifest, signature, and token files.
* `make distclean`: Clean up the source code and the installation directory.
