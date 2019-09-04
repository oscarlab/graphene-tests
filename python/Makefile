# Build the manifest for Python 2.7:
#
# - make                Building for Linux
# - make DEBUG=1        Building for Linux (with Graphene debug output)
# - make SGX=1          Building for SGX
# - make SGX=1 DEBUG=1  Building for SGX (with Graphene debug output)
#
# Use `make clean` to remove Graphene-generated files.

# Constants

# Installation location of Python. By default, Graphene will run the system Python
# executable.
PYTHONHOME ?= /usr/lib/python2.7
PYTHONEXEC ?= /usr/bin/python2.7

# numpy and scipy are included as trusted libraries by default. Overwrite the
# following variables to exclude these libraries.
USE_NUMPY ?= yes
USE_SCIPY ?= yes

# Relative path to Graphene root
GRAPHENEDIR ?= ../../../../..

ifeq ($(DEBUG),1)
GRAPHENEDEBUG = inline
else
GRAPHENEDEBUG = none
endif

.PHONY: all
all: python.manifest pal_loader
ifeq ($(SGX),1)
all: python.manifest.sgx python.token python.sig
endif

# Python dependencies (generate from ldd):
#
# For SGX, the manifest needs to list all the libraries loaded during the
# execution, so that the signer can include the file checksums.
#
# The dependencies are generated from the ldd results.

# We need to replace Glibc dependencies with Graphene-specific Glibc. The Glibc
# binaries are already listed in the manifest template, so we can skip them
# from the ldd results.
GLIBC_DEPS = linux-vdso /lib64/ld-linux-x86-64 libc libm librt libdl libpthread

# Define the python libraries which are dynamically loaded.
PY_LIBS = $(PYTHONHOME)/lib-dynload/_hashlib.x86_64-linux-gnu.so \
	  $(PYTHONHOME)/lib-dynload/_ctypes.x86_64-linux-gnu.so \
	  $(PYTHONHOME)/lib-dynload/_ssl.x86_64-linux-gnu.so

ifeq ($(USE_NUMPY),yes)
PY_LIBS += $(PYTHONHOME)/dist-packages/numpy/linalg/lapack_lite.x86_64-linux-gnu.so \
	   $(PYTHONHOME)/dist-packages/numpy/core/multiarray.x86_64-linux-gnu.so
endif

ifeq ($(USE_SCIPY),yes)
PY_LIBS += $(PYTHONHOME)/dist-packages/scipy/sparse/_sparsetools.x86_64-linux-gnu.so
endif

# Listing all the Python dependencies, besides Glibc libraries
.INTERMEDIATE: python-ldd
python-ldd:
	@for F in $(PY_LIBS); do ldd $$F >> $@ || exit 1; done

.INTERMEDIATE: python-deps
python-deps: python-ldd
	@cat $< | awk '{if ($$2 =="=>") {split($$1,s,/\./); print s[1]}}' \
		| sort | uniq | grep -v -x $(patsubst %,-e %,$(GLIBC_DEPS)) > $@

# Generating manifest rules for Python dependencies
.INTERMEDIATE: python-trusted-libs
python-trusted-libs: python-deps
	@PY_LIBS="$(PY_LIBS)" && \
	for F in `cat python-deps`; do \
		P=`ldd $$PY_LIBS | grep $$F | awk '{print $$3; exit}'`; \
		N=`echo $$F | tr --delete '+-'`; \
		echo -n "sgx.trusted_files.$$N = file:$$P\\\\n"; \
	done > $@

# Python manifests:
#   For each dependency, generate a rule as follows:
#       sgx.trusted_files.xxxx = file:xxxx

python.manifest: python.manifest.template python-trusted-libs
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		-e 's|$$(PYTHONHOME)|'"$(PYTHONHOME)"'|g' \
		-e 's|$$(PYTHONEXEC)|'"$(PYTHONEXEC)"'|g' \
		-e 's|$$(PYTHON_TRUSTED_LIBS)|'"`cat python-trusted-libs`"'|g' \
		$< > $@

# Python manifests for SGX:
#   Generating the SGX-specific manifest (python.manifest.sgx), the enclave signature,
#   and the token for enclave initialization.

python.manifest.sgx: python.manifest
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@

python.sig: python.manifest.sgx

python.token: python.sig
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output python.token -sig python.sig

# Extra executables
pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

.PHONY: test
test: all
	./run-tests.sh

.PHONY: clean
clean:
	$(RM) *.manifest *.manifest.sgx *.token *.sig pal_loader
