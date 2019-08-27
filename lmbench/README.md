# LMBench 2.5 example

This directory contains an example for running LMBench 2.5 in Graphene, including
the Makefile and a template for generating the manifest. The application is
tested on Ubuntu 16.04, with both normal Linux and SGX platforms.

# Generating the manifest

## Building for Linux

Run `make` (non-debug) or `make DEBUG=1` (debug) in the directory.

## Building for SGX

Run `make SGX=1` (non-debug) or `make SGX=1 DEBUG=1` (debug) in the directory.

# Running LMBench

## Running natively

To run the whole test suite natively, use one of the following commands:
```
make run-native

or

cd lmbench-2.5/scripts && env OS=linux ./results

```

To run individual tests, you may run the programs in `lmbench-2.5/bin/linux`.
Here are a few examples:
```
./lat_syscall null
./lat_syscall read
./lat_syscall write
```

## Running with Graphene

To run the whole test suite under Graphene, use one of the following commands:
```
make run-graphene

or

cd lmbench-2.5/scripts && env LOADER=./pal_loader OS=linux RESULTS=results/graphene ./results
```

To run individual tests, you may run the programs in `lmbench-2.5/bin/linux`,
using `pal_loader`. Here are a few examples:
```
./pal_loader lat_syscall null
./pal_loader lat_syscall read
./pal_loader lat_syscall write
```

## Running with Graphene-SGX

To run the whole test suite, use one of the following commands:
```
make run-graphene SGX=1

or

cd lmbench-2.5/scripts && env SGX=1 LOADER=./pal_loader OS=linux RESULTS=results/graphene ./results
```

To run individual tests, you may run the programs in `lmbench-2.5/bin/linux`,
using `pal_loader`. Here are a few examples:
```
SGX=1 ./pal_loader lat_syscall null
SGX=1 ./pal_loader lat_syscall read
SGX=1 ./pal_loader lat_syscall write
```
