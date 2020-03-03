# PyTorch

This directory contains steps and artifacts to run a PyTorch sample workload on Graphene. Specifically, this example uses a pre-trained model for image classification. We tested this on Ubuntu 16.04 and 18.04. The sample uses the package versions of Python (3.5 and 3.6) coming with each distribution.

The workload reads an image from a file on disk `input.jpg` and runs the classifier to detect what object is present in the image. For the image shipping with the workload, the output will be

```
[('Labrador retriever', 41.58518600463867), ('golden retriever', 16.59165382385254), ('Saluki, gazelle hound', 16.286855697631836), ('whippet', 2.853914976119995), ('Ibizan hound, Ibizan Podenco', 2.3924756050109863)]
```

With high probability (41%) the classifier detected the image to contain a Labrador retriever.

# Pre-requisites

The following steps should suffice to run the workload on a stock Ubuntu 16.04 and 18.04 installation.

- `sudo apt-get install python3-pip` to install `pip` which is required to install addition Python packages.
- `pip3 install --user torchvision` to install the torchvision Python package and its dependencies (usually in $HOME/.local). WARNING: This downloads several hundred megabytes of data!
- `python3 -c 'import torchvision ; torchvision.models.alexnet(pretrained=True)'` to download the pre-trained model ($HOME/.cache/torch). WARNING: Again, this downloads substantial amounts of data!

# Run

Execute any one of the following commands to run the workload

- natively: `python3 pytorchexample.py`
- with Graphene: `./pal_loader ./pytorch.manifest ./pytorchexample.py`
- with Graphene-SGX: `SGX=1 ./pal_loader ./pytorch.manifest ./pytorchexample.py`
