PYTHON_SRC = Python-2.7.9
PYTHON_INSTALL = $(PYTHON_SRC)/build

manifests = openvino_fpga.manifest

exec_target = $(manifests)

#extra_rules = -e 's:\$$(PYTHONDIR):$(PYTHON_INSTALL)/:g'
extra_rules = -e 's:\$$(PYTHONDIR):$(PYTHON_INSTALL)/:g' -e 's:\$$(HOME):$(HOME)/:g'



clean-extra += clean-tmp

level = ../../
include ../../Makefile

clean-tmp:
	rm -f openvino_fpga.manifest.sgx *.sig *.token

