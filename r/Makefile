# Build the manifest for R:
#
# - make
# - make DEBUG=1
# - make SGX=1
# - make SGX=1 DEBUG=1
#
# Use `make clean` to remove Graphene-generated files.

# Constants

# Installation location of R. By default, Graphene will run the system R executable.
R_HOME ?= /usr/lib/R
R_EXEC = $(R_HOME)/bin/exec/R

# Relative path to Graphene root
GRAPHENEDIR ?= ../../../../..

ifeq ($(DEBUG),1)
GRAPHENEDEBUG = inline
else
GRAPHENEDEBUG = none
endif

GREP = grep
LDD  = ldd
AWK  = awk

LD_LIBRARY_PATH := $(LD_LIBRARY_PATH):$(R_HOME)/lib
export LD_LIBRARY_PATH

.PHONY: all
all: R.manifest sh.manifest pal_loader
ifeq ($(SGX),1)
all: R.manifest.sgx sh.manifest.sgx
endif

# R dependencies (generate from ldd):
#
# For SGX, the manifest needs to list all the libraries loaded during the
# execution, so that the signer can include the file checksums.
#
# The dependencies are generated from the ldd results of:
#    - $(R_HOME)/bin/exec/R
#    - $(R_HOME)/library/stats/libs/stats.so
#    - $(R_HOME)/modules/lapack.so

# Skip the GLIBC libraries because they are already listed
GLIBC_DEPS = linux-vdso /lib64/ld-linux-x86-64 libc libm librt libdl libpthread

# Use the ldd result of R and stats.so
R_TARGETS = $(R_EXEC) $(R_HOME)/library/stats/libs/stats.so $(R_HOME)/modules/lapack.so

# Collect the dependencies (without repeats)
R_ALL_DEPS = $(shell $(LDD) $(R_TARGETS) | $(AWK) '{if ($$2 == "=>") {split ($$1,s,/\./); print s[1]}}' | sort | uniq)
R_DEPS = $(filter-out $(GLIBC_DEPS),$(R_ALL_DEPS))

# R manifests:
#   For each dependency, generate a rule as follows:
#       sgx.trusted_files.xxxx = file:xxxx

R.manifest: R.manifest.template
	for F in $(R_DEPS); do \
		P=`$(LDD) $(R_TARGETS) | $(GREP) $$F | $(AWK) '{print $$3; exit}'`; \
		F=`echo $$F | tr --delete '+'`; \
		R_TRUSTED_LIBS="$$R_TRUSTED_LIBS\nsgx.trusted_files.$$F = file:$$P"; \
		done && \
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		-e 's|$$(R_HOME)|'"$(R_HOME)"'|g' \
		-e 's|$$(R_EXEC)|'"$(R_EXEC)"'|g' \
		-e 's|$$(R_TRUSTED_LIBS)|'"$$R_TRUSTED_LIBS"'|g' \
		$< > $@

sh.manifest: sh.manifest.template
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		$< > $@

# R manifests for SGX:
#   Generating the SGX-specific manifest (R.manifest.sgx), the enclave signature,
#   and the token for enclave initialization.

R.manifest.sgx: R.manifest sh.manifest.sgx
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output R.token -sig R.sig

# sh.manifest.sgx is needed for R to run the shell for file clean-up
sh.manifest.sgx: sh.manifest
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output sh.token -sig sh.sig


# Extra executables
pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

# Clean up
.PHONY: clean
clean:
	$(RM) *.manifest *.manifest.sgx *.token *.sig pal_loader
