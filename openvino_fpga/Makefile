PYTHON_SRC = Python-2.7.9
PYTHON_INSTALL = $(PYTHON_SRC)/build

manifests = openvino_fpga.manifest

exec_target = $(manifests)

# HARDLINK needs to be updated to point the FPGA device file on the system.
# find /sys/devices/ -name "fpga"
# The Makefile updates $(HARDLINK) in the manifest to point to the location of device file objects which may change from system to system
DEVICEPATH = /sys/devices/pci0000:00/0000:00:01.1/0000:02:00.0/fpga
#extra_rules = -e 's:\$$(PYTHONDIR):$(PYTHON_INSTALL)/:g'
extra_rules = -e 's:\$$(PYTHONDIR):$(PYTHON_INSTALL)/:g' -e 's:\$$(HOME):$(HOME)/:g' -e 's|\$$(DEVICEPATH)|$(DEVICEPATH)|g'



clean-extra += clean-tmp

level = ../../
include ../../Makefile

clean-tmp:
	rm -f openvino_fpga.manifest.sgx *.sig *.token

