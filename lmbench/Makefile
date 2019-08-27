# Build the manifest for LMBench 2.5:
#
# - make
# - make DEBUG=1
# - make SGX=1
# - make SGX=1 DEBUG=1
#
# Use `make clean` to remove Graphene-generated files.

# Constants

# Source code and install directory of LMBench
LMBENCHDIR = lmbench-2.5
INSTALLDIR = $(LMBENCHDIR)/bin/linux
LMBENCHCONFIG = $(INSTALLDIR)$(shell $(LMBENCHDIR)/scripts/config)

# Relative path to Graphene root
GRAPHENEDIR ?= ../../../../..

# If GRAPHENEDIR is a relative path, extend the path from where LMBench is installed
ifeq ($(patsubst /%,,$(GRAPHENEDIR)),)
GRAPHENEDIR_FROM_INSTALLDIR = $(GRAPHENEDIR)
else
GRAPHENEDIR_FROM_INSTALLDIR = ../../../$(GRAPHENEDIR)
endif

ifeq ($(DEBUG),1)
GRAPHENEDEBUG = inline
else
GRAPHENEDEBUG = none
endif

MANIFESTS = $(INSTALLDIR)/manifest $(INSTALLDIR)/hello.manifest $(INSTALLDIR)/sh.manifest

.PHONY: all
all: $(INSTALLDIR) $(MANIFESTS) $(INSTALLDIR)/pal_loader
ifeq ($(SGX),1)
all: sgx
endif

export CC
export CFLAGS

# Building LMBench 2.5

$(INSTALLDIR):
	$(MAKE) -C $(LMBENCHDIR)/src OS=linux

$(INSTALLDIR)/lmbench-test-ci:
	cp lmbench-test-ci $@

# Generating the manifests

$(MANIFESTS): $(INSTALLDIR)/%: %.template $(INSTALLDIR)
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR_FROM_INSTALLDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		$< > $@

# Generating the manifests for SGX
#
# For each program in LMBench, we need to generate the manifest
# individually, along with the signature and the inittoken.
#
# The 'sgx' rule below will list the executables in $(INSTALLDIR)
# and generate their manifests for SGX.

.PHONY: sgx
sgx: $(INSTALLDIR) $(INSTALLDIR)/sh.manifest.sgx $(INSTALLDIR)/hello.manifest.sgx
	cd $(INSTALLDIR) && \
	for f in `find -executable -not -name . -not -name lmbench -not -name hello`; do \
		if [ ! -f $$f.manifest.sgx ]; then \
			$(GRAPHENEDIR_FROM_INSTALLDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
				-libpal $(GRAPHENEDIR_FROM_INSTALLDIR)/Runtime/libpal-Linux-SGX.so \
				-key $(GRAPHENEDIR_FROM_INSTALLDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
				-manifest manifest -output $$f.manifest.sgx && \
			$(GRAPHENEDIR_FROM_INSTALLDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
				-output $$f.token -sig $$f.sig; \
		fi; \
	done

$(INSTALLDIR)/sh.manifest.sgx $(INSTALLDIR)/hello.manifest.sgx: %.sgx: %
	cd $(INSTALLDIR) && \
	$(GRAPHENEDIR_FROM_INSTALLDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR_FROM_INSTALLDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR_FROM_INSTALLDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $(abspath $<) -output $(abspath $@) && \
	$(GRAPHENEDIR_FROM_INSTALLDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output $(abspath $(basename $<).token) -sig $(abspath $(basename $<).sig)

# Running LMBench natively and under Graphene
#
# - make run-native:   run the whole test suite natively (with configuration)
# - make run-graphene: run the whole test suite under Graphene (with configuration)
# - make test:         run LMBench for CI (without configuration)

$(LMBENCHCONFIG):
	cd $(LMBENCHDIR)/scripts && env OS=linux ./config-run

.PHONY: run-native
run-native: all $(LMBENCHCONFIG)
	cd $(LMBENCHDIR)/scripts && env OS=linux ./results

.PHONY: run-graphene
run-graphene: all $(LMBENCHCONFIG)
	cd $(LMBENCHDIR)/scripts && env LOADER=./pal_loader OS=linux RESULTS=results/graphene ./results

.PHONY: test
test: all $(INSTALLDIR)/lmbench-test-ci
	cd $(INSTALLDIR) && env LOADER=./pal_loader OS=linux ./lmbench-test-ci

$(INSTALLDIR)/pal_loader:
	ln -s $(GRAPHENEDIR_FROM_INSTALLDIR)/Runtime/pal_loader $@

.PHONY: clean
clean:
	$(MAKE) -C $(LMBENCHDIR) clean
