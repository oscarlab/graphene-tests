This example demonstrates how to run Tensorflow (v1.9) Lite's label_image example on Graphene.

Tested on Ubuntu 16.04 with Graphene's chiache/glibc-2.23 branch. Building Tensorflow on Ubuntu 16.04 creates dependencies on this newer glibc.

Install build dependencies with `make install-dependencies-ubuntu`.

Build everything with `SGX=1 make && SGX_RUN=1 make`.

Run the example with `SGX=1 make check`.
