manifests = $(addsuffix .manifest,label_image)
exec_target = $(manifests)
target = label_image

GRAPHENEDIR=../../../../..
TF_DIR ?= tensorflow
BAZEL_BIN ?= $(HOME)/bin/bazel

tensorflow/configure:
	git clone https://github.com/tensorflow/tensorflow
	cd tensorflow && git checkout tags/v1.9.0

tensorflow/bazel-bin/tensorflow/contrib/lite/examples/label_image/label_image: tensorflow/configure
	cd tensorflow && $(BAZEL_BIN) build tensorflow/contrib/lite/examples/label_image

label_image: $(TF_DIR)/bazel-bin/tensorflow/contrib/lite/examples/label_image/label_image
	cp $^ .

libtensorflow_framework.so: label_image
	$(RM) $@
	cp $(TF_DIR)/bazel-bin/tensorflow/libtensorflow_framework.so $@

inception_v3.tflite:
	wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/model_zoo/upload_20180427/inception_v3_2018_04_27.tgz
	tar xfz inception_v3_2018_04_27.tgz

labels.txt: tensorflow/tensorflow/contrib/lite/java/ovic/src/testdata/labels.txt
	cp $^ $@

image.bmp: tensorflow/tensorflow/contrib/lite/examples/label_image/testdata/grace_hopper.bmp
	cp $^ $@

../../../../../Runtime/libgcc_s.so.1:
	cp /lib/x86_64-linux-gnu/libgcc_s.so.1 $@

../../../../../Runtime/libstdc++.so.6:
	cp /usr/lib/x86_64-linux-gnu/libstdc++.so.6 $@

label_image.manifest: label_image.manifest.template
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		$< > $@

label_image.manifest.sgx: libtensorflow_framework.so label_image
label_image.manifest.sgx: inception_v3.tflite
label_image.manifest.sgx: labels.txt
label_image.manifest.sgx: image.bmp
label_image.manifest.sgx: ../../../../../Runtime/libgcc_s.so.1 ../../../../../Runtime/libstdc++.so.6

label_image.manifest.sgx: label_image.manifest label_image
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@ \
		-exec label_image
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output label_image.token -sig label_image.sig

.PHONY: check
ifeq ($(SGX),1)
check: label_image.manifest.sgx
else
check: label_image.manifest
endif
	./pal_loader ./label_image.manifest.sgx -m inception_v3.tflite -i image.bmp -t 1

.PHONY: clean
clean:
	$(RM) -f label_image.manifest label_image.manifest.sgx label_image.sig label_image.token

.PHONY: distclean
distclean: clean
	$(RM) -rf label_image
	$(RM) inception_v3_2018_04_27.tgz inception_v3.pb inception_v3.tflite labels.txt image.bmp
	$(RM) -rf tensorflow

.PHONY: install-dependencies-ubuntu
install-dependencies-ubuntu:
	apt-get update
	apt-get install -y python-dev python-pip wget git
# https://docs.bazel.build/versions/master/install-ubuntu.html
	apt-get install -y pkg-config zip g++ zlib1g-dev unzip python
	wget https://github.com/bazelbuild/bazel/releases/download/0.16.1/bazel-0.16.1-installer-linux-x86_64.sh
	chmod +x bazel-0.16.1-installer-linux-x86_64.sh
	./bazel-0.16.1-installer-linux-x86_64.sh --user
