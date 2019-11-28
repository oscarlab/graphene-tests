# Building the manifest for nodejs:
#
# - make                  Building for Linux
# - make DEBUG=1          Building for Linux, with Graphene debug output
# - make SGX=1            Building for SGX
# - make SGX=1 DEBUG=1    Building for SGX, with Graphene debug output
#
# Use `make clean` to remove Graphene-generated files.
#
# Use `make distclean` to further remove the Nginx tarball, source code,
# and installation.

THIS_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
ifeq ($(THIS_DIR), ./)  # workaround Graphene issue #1044 with allowed_files
THIS_DIR :=
endif

# Relative path to Graphene root
GRAPHENEDIR ?= $(THIS_DIR)../../../../..

ifeq ($(DEBUG),1)
GRAPHENEDEBUG = inline
else
GRAPHENEDEBUG = none
endif

.PHONY: all
all: nodejs.manifest pal_loader
ifeq ($(SGX),1)
all: nodejs.manifest.sgx nodejs.sig nodejs.token
endif

nodejs.manifest: nodejs.manifest.template
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
        -e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		$< > $@

# Generating the SGX-specific manifest (nodejs.manifest.sgx), the enclave signature,
# and the token for enclave initialization.
nodejs.manifest.sgx: nodejs.manifest
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@

nodejs.sig: nodejs.manifest.sgx

nodejs.token: nodejs.sig
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output nodejs.token -sig nodejs.sig

# Extra executables
pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

.PHONY: clean
clean:
	$(RM) *.manifest *.manifest.sgx *.token *.sig pal_loader
