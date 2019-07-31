# Build LightGBM as follows:
#
# - make               -- create non-SGX no-debug-log manifest
# - make SGX=1         -- create SGX no-debug-log manifest
# - make SGX=1 DEBUG=1 -- create SGX debug-log manifest
#
# Any of these invocations clones LightGBM git repository and builds LightGBM
# in default configuration and in the latest (master branch) version.
#
# Use `make clean` to remove Graphene-generated files and `make distclean` to
# additionally remove the cloned LightGBM git repository.

 ################################# CONSTANTS ###################################

 # Relative path to Graphene root
GRAPHENE = ../../../../..
GRAPHENEDIR = $(abspath $(GRAPHENE))

SRCDIR = LightGBM
COMMIT = master

 ifeq ($(DEBUG),1)
GRAPHENEDEBUG = inline
else
GRAPHENEDEBUG = none
endif


 .PHONY=all
all: lightgbm lightgbm.manifest pal_loader
ifeq ($(SGX),1)
all: lightgbm.manifest.sgx
endif

 ############################ LightGBM EXECUTABLE #############################

 # LightGBM is built as usual, without any changes to the build process. The
# source is cloned from a public GitHub repo (master tip) and built via classic
# ./autogen.sh && ./configure && make. The result of this build process is
# the final executable "src/LightGBM".

 $(SRCDIR):
	git clone --recursive https://github.com/microsoft/LightGBM $(SRCDIR)
	cd $(SRCDIR) && git checkout $(COMMIT)
	cd $(SRCDIR) && mkdir -p build
	cd $(SRCDIR)/build && cmake ..

 $(SRCDIR)/lightgbm: $(SRCDIR)
	cd $(SRCDIR)/build && make

 ############################## LightGBM MANIFEST #############################

 # The template file contains almost all necessary information to run LightGBM
# under Graphene / Graphene-SGX. We create LightGBM.manifest (to be run under
# non-SGX Graphene) by simply replacing variables in the template file via sed.

 lightgbm.manifest: lightgbm.manifest.template
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
	    -e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
        -e 's|$$(PALLOADER)|'"$(abspath $(GRAPHENEDIR)/Runtime/pal_loader)"'|g' \
	    $< > $@
	    chmod 777 $@

 # Manifest for Graphene-SGX requires special "pal-sgx-sign" procedure. This
# procedure measures all LightGBM dependencies (shared libraries and trusted
# files), measures LightGBM code/data pages, and adds measurements in the
# resulting manifest.sgx file (among other, less important SGX options).
#
# Additionally, Graphene-SGX requires EINITTOKEN and SIGSTRUCT objects (see
# SGX hardware ABI, in particular EINIT instruction). The "pal-sgx-get-token"
# script generates these objects and puts them in files .token and .sig
# respectively. Note that filenames must be the same as the executable/manifest
# name (i.e., "LightGBM").

 lightgbm.manifest.sgx: lightgbm.manifest $(SRCDIR)/lightgbm
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@ \
		-exec $(SRCDIR)/lightgbm
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output lightgbm.token -sig lightgbm.sig

 ########################### COPIES OF EXECUTABLES #############################

 # LightGBM build process creates the final executable as src/LightGBM. For
# simplicity, copy it into our root directory.
# Also, create a link to pal_loader for simplicity.

 lightgbm: $(SRCDIR)/lightgbm 
	cp -p $(SRCDIR)/lightgbm lightgbm
	cp -prf $(SRCDIR)/examples/ examples/

 pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

 ################################## CLEANUP ####################################

 .PHONY=clean
clean:
	$(RM) *.token *.sig *.manifest.sgx *.manifest pal_loader lightgbm

 .PHONY=distclean
distclean: clean
	$(RM) -r $(SRCDIR)



