manifests = $(addsuffix .manifest,label_image)
exec_target = $(manifests)
target = label_image

level = ../../
include ../../Makefile

clean_extra += clean_tmp

label_image.manifest.sgx: libtensorflow_framework.so label_image
label_image.manifest.sgx: inception_v3.tflite
label_image.manifest.sgx: labels.txt
label_image.manifest.sgx: image.bmp
label_image.manifest.sgx: ../../../../../Runtime/libgcc_s.so.1 ../../../../../Runtime/libstdc++.so.6

libtensorflow_framework.so:
	$(MAKE) -f label_image.make $@

label_image:
	$(MAKE) -f label_image.make $@

inception_v3.tflite:
	$(MAKE) -f label_image.make $@

labels.txt:
	$(MAKE) -f label_image.make $@

image.bmp:
	$(MAKE) -f label_image.make $@

../../../../../Runtime/libgcc_s.so.1:
	cp /lib/x86_64-linux-gnu/libgcc_s.so.1 $@

../../../../../Runtime/libstdc++.so.6:
	cp /usr/lib/x86_64-linux-gnu/libstdc++.so.6 $@

.PHONY: check
check:
	./pal_loader ./label_image.manifest.sgx -m inception_v3.tflite -i image.bmp -t 1

.PHONY: clean-tmp
clean-tmp:
	$(MAKE) -f label_image.make clean

.PHONY: distclean
distclean: clean
	$(MAKE) -f label_image.make $@
