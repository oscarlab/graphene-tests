# Build the manifest for Python 2.7:
#
# - make
# - make DEBUG=1
# - make SGX=1
# - make SGX=1 DEBUG=1
#
# Use `make clean` to remove Graphene-generated files.

# Constants

# Installation location of Python. By default, Graphene will run the system Python
# executable.
PYTHONHOME ?= /usr/lib/python2.7
PYTHONEXEC ?= /usr/bin/python2.7

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
all: python.manifest pal_loader
ifeq ($(SGX),1)
all: python.manifest.sgx
endif

# Python dependencies (generate from ldd):
#
# For SGX, the manifest needs to list all the libraries loaded during the
# execution, so that the signer can include the file checksums.
#
# The dependencies are generated from the ldd results.
#
# Define the dynamic libraries to load (mainly for numpy, scipy, and http):

PY_LIBS = $(PYTHONHOME)/dist-packages/numpy/linalg/lapack_lite.x86_64-linux-gnu.so \
	  $(PYTHONHOME)/dist-packages/numpy/core/multiarray.x86_64-linux-gnu.so \
	  $(PYTHONHOME)/dist-packages/scipy/sparse/_sparsetools.x86_64-linux-gnu.so \
	  $(PYTHONHOME)/lib-dynload/_hashlib.x86_64-linux-gnu.so \
	  $(PYTHONHOME)/lib-dynload/_ctypes.x86_64-linux-gnu.so \
	  $(PYTHONHOME)/lib-dynload/_ssl.x86_64-linux-gnu.so

# Skip the GLIBC libraries because they are already listed
GLIBC_DEPS = linux-vdso /lib64/ld-linux-x86-64 libc libm librt libdl libpthread

# Collect the dependencies (without repeats)
PY_ALL_DEPS = $(shell $(LDD) $(PY_LIBS) | $(AWK) '{if ($$2 == "=>") {split ($$1,s,/\./); print s[1]}}' | sort | uniq)
PY_DEPS = $(filter-out $(GLIBC_DEPS),$(PY_ALL_DEPS))

# Python manifests:
#   For each dependency, generate a rule as follows:
#       sgx.trusted_files.xxxx = file:xxxx

python.manifest: python.manifest.template
	PY_LIBS="$(PY_LIBS)" && \
	for F in $(PY_DEPS); do \
		P=`$(LDD) $$PY_LIBS | $(GREP) $$F | $(AWK) '{print $$3; exit}'`; \
		F=`echo $$F | tr --delete '+'`; \
		PYTHON_TRUSTED_LIBS="$$PYTHON_TRUSTED_LIBS\nsgx.trusted_files.$$F = file:$$P"; \
		done && \
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		-e 's|$$(PYTHONHOME)|'"$(PYTHONHOME)"'|g' \
		-e 's|$$(PYTHONEXEC)|'"$(PYTHONEXEC)"'|g' \
		-e 's|$$(PYTHON_TRUSTED_LIBS)|'"$$PYTHON_TRUSTED_LIBS"'|g' \
		$< > $@

# Python manifests for SGX:
#   Generating the SGX-specific manifest (python.manifest.sgx), the enclave signature,
#   and the token for enclave initialization.

python.manifest.sgx: python.manifest
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output python.token -sig python.sig


# Extra executables
pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

regression:
	@echo "\n\nBuilding Python..."
	@$(MAKE) >> /dev/null 2>&1

	@echo "\n\nRun helloworld.py:"
	./pal_loader python.manifest scripts/helloworld.py > OUTPUT
	$(GREP) -q "Hello World" OUTPUT
	@$(RM) OUTPUT

	@echo "\n\nRun fibonacci.py:"
	./pal_loader python.manifest scripts/fibonacci.py  > OUTPUT
	$(GREP) -q "fib2              55" OUTPUT
	@$(RM) -f OUTPUT

	@echo "\n\nRun test-numpy.py:"
	./pal_loader python.manifest scripts/test-numpy.py

	@echo "\n\nRun test-scipy.py:"
	./pal_loader python.manifest scripts/test-scipy.py

	./web-test.sh

# Clean up
.PHONY: clean
clean:
	$(RM) *.manifest *.manifest.sgx *.token *.sig pal_loader
