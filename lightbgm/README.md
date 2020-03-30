# Steps to run LightBGM on Graphene and Graphene SGX

To run LightBGM, first prepare the manifest:
```
cd <Graphene directory>/LibOS/shim/test/apps/lightbgm
make clean
make (In case of Graphene SGX, make SGX=1 and make SGX_RUN=1)
```

You can run `lightgbm.manifest` or `lightgbm.manifest.sgx` as an executable to run on any machine learning data.

Copy the manifest file to any one of the examples directory which contains different machine learning models.
For example,
```
cp -p lightgbm.manifest examples/binary_classification/
```

Use the following commands to run the binary:
```
cd examples/binary_classification/
./lightgbm.manifest config=train.conf
```

This generates a trained model stored in `LightGBM_model.txt`.

To predict the data with the trained model, run:
```
./lightgbm.manifest config=predict.conf
```

The result can be found in `LightGBM_predict_result.txt`.

