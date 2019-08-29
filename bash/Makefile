# Build the manifests for Bash:
#
# - make
# - make DEBUG=1
# - make SGX=1
# - make SGX=1 DEBUG=1
#
# Use `make clean` to remove Graphene-generated files.

# Constants

# Listing the programs to be run inside the bash script
PROGRAMS = ls cat rm cp date

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

.PHONY: all
all: bash.manifest $(addsuffix .manifest,$(PROGRAMS)) pal_loader
ifeq ($(SGX),1)
all: bash.manifest.sgx $(addsuffix .manifest.sgx,$(PROGRAMS))
endif

# Program dependencies (generate from ldd):
#
# For SGX, the manifest needs to list all the libraries loaded during the
# execution, so that the signer can include the file checksums.
#
# The dependencies are generated from the ldd results.

# Skip the GLIBC libraries because they are already listed
GLIBC_DEPS = linux-vdso /lib64/ld-linux-x86-64 libc libm librt libdl libpthread

# Listing all the Apache dependencies, besides Glibc libraries
.INTERMEDIATE: $(addsuffix .deps,bash $(PROGRAMS))
%.deps:
	$(LDD) $(shell which $(basename $@)) | \
		$(AWK) '{if ($$2 =="=>") {split($$1,s,/\./); print s[1]}}' | \
		($(GREP) -v -x $(patsubst %,-e %,$(GLIBC_DEPS)) || true) > $@

# Generating manifest rules for Apache dependencies
.INTERMEDIATE: $(addsuffix .trusted-libs,bash $(PROGRAMS))
%.trusted-libs: %.deps
	for F in `cat $<`; do \
		P=`$(LDD) $(shell which $(basename $@)) | $(GREP) $$F | $(AWK) '{print $$3; exit}'`; \
		N=`echo $$F | tr --delete '-'`; \
		echo -n "sgx.trusted_files.$$N = file:$$P\\\\n"; \
	done > $@

.INTERMEDIATE: trusted-children
trusted-children:
	@for F in $(PROGRAMS); do \
		echo -n "sgx.trusted_children.$$F = file:$$F.sig\\\\n"; \
		echo -n "sgx.trusted_files.$$F    = file:`which $$F`\\\\n"; \
		done > $@

bash.manifest: manifest.template trusted-children bash.trusted-libs
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		-e 's|$$(EXECNAME)|bash|g' \
		-e 's|$$(EXECPATH)|'"$(shell which bash)"'|g' \
		-e 's|$$(TRUSTED_LIBS)|'"`cat bash.trusted-libs`"'|g' \
		-e 's|$$(TRUSTED_CHILDREN)|'"`cat trusted-children`"'|g' \
		$< > $@

$(addsuffix .manifest,$(PROGRAMS)): %.manifest: manifest.template %.trusted-libs
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		-e 's|$$(EXECNAME)|'"$(basename $@)"'|g' \
		-e 's|$$(EXECPATH)|'"$(shell which $(basename $@))"'|g' \
		-e 's|$$(TRUSTED_LIBS)|'"`cat $(basename $@).trusted-libs`"'|g' \
		-e 's|$$(TRUSTED_CHILDREN)||g' \
		$< > $@

# Manifests for SGX:
#   Generating the SGX-specific manifest (*.manifest.sgx), the enclave signature,
#   and the token for enclave initialization.

bash.manifest.sgx: bash.manifest $(addsuffix .manifest.sgx,$(PROGRAMS))
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output bash.token -sig bash.sig

$(addsuffix .manifest.sgx,$(PROGRAMS)): %.manifest.sgx: %.manifest
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output $(basename $<).token -sig $(basename $<).sig


# Extra executables
pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

.PHONY: test
test: all
	@echo "\n\nRun \"ls\":"
	./pal_loader bash.manifest -c "ls" > OUTPUT
	@echo "[ Success ]"
	@rm OUTPUT

	@echo "\n\nRun bash_test.sh (2 iterations):"
	./pal_loader bash.manifest -c "cd scripts && bash bash_test.sh 2"
	@grep -q "hello 2" scripts/OUTPUT && echo "[ Success ]"
	@rm scripts/OUTPUT

	@echo "\n\nRun bash_test.sh (100 iterations):"
	./pal_loader bash.manifest -c "cd scripts && bash bash_test.sh 100"
	@grep -q "hello 100" scripts/OUTPUT && echo "[ Success ]"
	@rm scripts/OUTPUT

.PHONY: clean
clean:
	$(RM) *.manifest *.manifest.sgx *.token *.sig pal_loader
