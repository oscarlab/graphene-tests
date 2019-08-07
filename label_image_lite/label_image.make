TF_DIR ?= tensorflow

BAZEL_BIN=$(HOME)/bin/bazel

.PHONY=default
default: label_image

.PHONY=install-dependencies-ubuntu
install-dependencies-ubuntu:
	apt-get update && apt-get -y upgrade
	apt-get install -y python-dev python-pip
	apt-get install -y wget git
# https://docs.bazel.build/versions/master/install-ubuntu.html
	apt-get install -y pkg-config zip g++ zlib1g-dev unzip python
	wget https://github.com/bazelbuild/bazel/releases/download/0.16.1/bazel-0.16.1-installer-linux-x86_64.sh
	chmod +x bazel-0.16.1-installer-linux-x86_64.sh
	./bazel-0.16.1-installer-linux-x86_64.sh --user

libtensorflow_framework.so: $(TF_DIR)/bazel-bin/tensorflow/libtensorflow_framework.so
	$(RM) $@
	cp $^ .

label_image: $(TF_DIR)/bazel-bin/tensorflow/contrib/lite/examples/label_image/label_image
	cp $^ .

tensorflow/configure:
	git clone https://github.com/tensorflow/tensorflow
	cd tensorflow && git checkout tags/v1.9.0

tensorflow/bazel-bin/tensorflow/contrib/lite/examples/label_image/label_image: tensorflow/configure
	cd tensorflow && $(BAZEL_BIN) build tensorflow/contrib/lite/examples/label_image

inception_v3.tflite:
	wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/model_zoo/upload_20180427/inception_v3_2018_04_27.tgz
	tar xfz inception_v3_2018_04_27.tgz

labels.txt: tensorflow/tensorflow/contrib/lite/java/ovic/src/testdata/labels.txt
	cp $^ $@

image.bmp: tensorflow/tensorflow/contrib/lite/examples/label_image/testdata/grace_hopper.bmp
	cp $^ $@

.PHONY=check
check:
	./pal_loader ./label_image.manifest.sgx  -m inception_v3.tflite -i image.bmp -t 1

.PHONY=clean-tmp
clean-tmp:
	$(RM) libtensorflow_framework.so

.PHONY=mrproper
mrproper: clean-tmp
	$(RM) inception_v3_2018_04_27.tgz inception_v3.pb inception_v3.tflite labels.txt image.bmp
	$(RM) -rf tensorflow
