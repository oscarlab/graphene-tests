Steps to run LightBGM on Graphene and Graphene SGX

To run LightBGM, first prepare the manifest:

cd LibOS/shim/test/apps/lightbgm
make clean
make (In case of Graphene SGX, run make SGX=1 and make SGX_RUN=1)

You can run lightgbm.manifest or lightgbm.manifest.sgx as an executable to run on any machine learning data.
Copy the manifest file to any one of the examples directory.

For example,
cp -p lightgbm.manifest examples/binary_classification/

Use the following commands to run the binary:

cd examples/binary_classification/
./lightgbm.manifest config=train.conf (To train the model)

This generates a model stored in LightGBM_model.txt.

To predict the data with the trained model, run:

./lightgbm.manifest config=predict.conf (To predict the model)

The result can be found in LightGBM_predict_result.txt.


