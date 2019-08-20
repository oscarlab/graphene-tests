# R example

This directory contains an example for running R in Graphene, including the
Makefile and a template for generating the manifest. The application is
tested on Ubuntu 16.04, with both normal Linux and SGX platforms.

# Generating the manifest

## Build for Linux

Run `make` (non-debug) or `make DEBUG=1` (debug) in the directory.

## Build for SGX

Run `make SGX=1` (non-debug) or `make SGX=1 DEBUG=1` (debug) in the directory.

## Build with a local R installation

By default, the `make` command build the manifest against the system R binary.
If you have a local R installation directly compiled from the source code, you
may build the manifest with the `R_HOME` variable. For example:

```
make R_HOME=<install path>/lib/R SGX=1
```

# Run R with Graphene

When running R with Graphene, please use the `--vanilla` or `--no-save` option.

Here's an example of running a R script into Graphene:

Without SGX:
```
./pal_loader R.manifest --slave --vanilla -f scripts/sample.r
./pal_loader R.manifest --slave --vanilla -f scripts/R-benchmark-25.R
```

With SGX:
```
SGX=1 ./pal_loader R.manifest --slave --vanilla -f scripts/sample.r
SGX=1 ./pal_loader R.manifest --slave --vanilla -f scripts/R-benchmark-25.R
```
