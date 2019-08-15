This example demonstrates how to run Tensorflow (v1.9) Lite's label_image example on Graphene. Reads an input image `image.bmp` from the current directory and uses Tensorflow lite and the Inception v3 model to label the image.

Known limitations:

- Tested on Ubuntu 16.04 with Graphene's chiache/glibc-2.23 branch. Building Tensorflow on Ubuntu 16.04 creates dependencies on this newer glibc. Ubuntu 18.04 should work, but have not tested.
- Currently single threaded. Multi-threaded not tested.

Install build dependencies with `make install-dependencies-ubuntu`.

Build everything with `SGX=1 make && SGX_RUN=1 make`.

Run the example with `SGX=1 make check`.
