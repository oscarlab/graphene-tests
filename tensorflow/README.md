This example demonstrates how to run Tensorflow (v1.9) Lite's label_image example on Graphene. Reads an input image `image.bmp` from the current directory and uses Tensorflow lite and the Inception v3 model to label the image.

Known limitations:

- Tested on Ubuntu 16.04 with Graphene [commit 030a088](https://github.com/oscarlab/graphene/tree/030a0888926f315710da94ee6f855c466059cf6c). Ubuntu 18.04 should work, but have not tested.
- Currently single threaded. Multi-threaded not tested.

Install build dependencies with `make install-dependencies-ubuntu`.

Build everything with `SGX=1 make all sgx-tokens`.

Run the example with `SGX=1 make check`.
