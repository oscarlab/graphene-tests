# OpenVINO

This directory contains a Makefile and a template manifest for 
OpenVINO toolkit with FPGA plugin (as of this writing, `version 2019_R3.1`).
We use the `benchmark_app` example from the OpenVINO distribution as a concrete application running
under Graphene-SGX. We test OpenVINO with offload to the FPGA (Plugin: Hetero:FPGA, CPU).

This was tested on a machine with SGX and Ubuntu 16.04.

# Prerequisites

1. Accelerator Stack RTE installed in the default install directory 

2. OpenVINO R3.1 installed in the default directory

3. Copy the following :
    Benchmark App copied to `./`
    Copy model to be tested to `./models/ `
        For e.g. squeenzenet or Resnet 50. Refer to the Model zoo and Optimizer guide on the OpenVINO website
    Copy image to be tested to `./pics/`
    Copy Shared library dependencies to `./lib`
        Refer to the manifest section: `sgx.trusted_files.*` for information on what all shared libraries need to be copied.

# Quick Start

```sh
# Build OpenVINO-FPGA with graphene-SGX;
make SGX=1

# run original OpenVINO/object_detection_sample_ssd
# note that this assumes the Release build of OpenVINO (no DEBUG=1)

# run OpenVINO/benchmark_app in non-SGX Graphene

   ./benchmark_app -d HETERO:FPGA,CPU -i ./pics/car.png -m ./models/squeezenet1.1.xml -api sync -niter 1 -nireq 1 -nstreams 1

# run OpenVINO/benchmark_app in Graphene-SGX

    SGX=1 ./openvino_fpga.manifest.sgx -d HETERO:FPGA,CPU -i ./pics/car.png -m ./models/squeezenet1.1.xml -api sync -niter 1 -nireq 1 -nstreams 1

Refer to the online OpenVINO document on benchmark_app regarding more information on output and configurable parameters
```
