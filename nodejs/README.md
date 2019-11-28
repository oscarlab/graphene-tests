# nodejs

This directory contains the Makefile and the template manifest for the nodejs
(apt-get install nodejs, version v8.10.0). This
was tested on a machine with SGX v1 and Ubuntu 18.04.

The Makefile and the template manifest contain extensive comments. Please review
them to understand the requirements for nodejs running under Graphene-SGX.

We install nodejs from apt.
On Ubuntu 18.04, Please run the following command to install nodejs:
```sh
sudo apt-get install -y nodejs
```

# Quick Start

```sh
# build nodejs and the final manifest
make SGX=1

# run nodejs in non-SGX Graphene
./pal_loader nodejs.manifest helloworld.js

# run nodejs in Graphene-SGX
SGX=1 ./pal_loader nodejs.manifest helloworld.js
```
