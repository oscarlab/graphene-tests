# Build busybox as follows:
#
# - make               -- create non-SGX no-debug-log manifest
# - make DEBUG=1       -- create non-SGX debug-log manifest
# - make SGX=1         -- create SGX no-debug-log manifest
# - make SGX=1 DEBUG=1 -- create SGX debug-log manifest
#
# Any of these invocations clones busybox git repository and builds it
# in the configuration according to default.config, in the latest (master
# branch) version.
#
# Use `make clean` to remove Graphene-generated files and `make distclean` to
# additionally remove the cloned busybox git repository.

################################# CONSTANTS ###################################

# Relative path to Graphene root
GRAPHENEDIR = ../../../../..

SRCDIR = src
COMMIT = master

ifeq ($(DEBUG),1)
GRAPHENEDEBUG = inline
else
GRAPHENEDEBUG = none
endif


.PHONY: all
all: busybox busybox.manifest pal_loader
ifeq ($(SGX),1)
all: busybox.manifest.sgx
endif

############################ BUSYBOX EXECUTABLE ###############################

# Busybox is built as usual, without any changes to the build process. The
# source is cloned from a public repo and built via classic make, using
# predefined config file ".config" (just for convenience). The result of this
# build process is the final executable "src/busybox".


$(SRCDIR)/.config:
	git clone git://busybox.net/busybox.git $(SRCDIR)
	cd $(SRCDIR) && git checkout $(COMMIT)
	cp default.config $(SRCDIR)/.config

$(SRCDIR)/busybox: $(SRCDIR)/.config
	cd $(SRCDIR) && make

############################## BUSYBOX MANIFEST ###############################

# The template file contains almost all necessary information to run Busybox
# under Graphene / Graphene-SGX. We create busybox.manifest (to be run under
# non-SGX Graphene) by simply replacing variables in the template file via sed.

busybox.manifest: busybox.manifest.template
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		$< > $@

# Manifest for Graphene-SGX requires special "pal-sgx-sign" procedure. This
# procedure measures all Busybox dependencies (shared libraries and trusted
# files), measures Busybox code/data pages, and adds measurements into the
# resulting manifest.sgx file (among other, less important SGX options).
#
# Additionally, Graphene-SGX requires EINITTOKEN and SIGSTRUCT objects (see
# SGX hardware ABI, in particular EINIT instruction). The "pal-sgx-get-token"
# script generates these objects and puts them in files .token and .sig
# respectively. Note that filenames must be the same as the executable/manifest
# name (i.e., "busybox").

busybox.manifest.sgx: busybox.manifest $(SRCDIR)/busybox
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@ \
		-exec $(SRCDIR)/busybox
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output busybox.token -sig busybox.sig

########################### COPIES OF EXECUTABLES #############################

# Busybox build process creates the final executable as "src/busybox". For
# simplicity, copy it into our root directory.
# Also, create a link to pal_loader for simplicity.

busybox: $(SRCDIR)/busybox
	cp $< $@

pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

################################## CLEANUP ####################################

.PHONY: clean
clean:
	$(RM) *.token *.sig *.manifest.sgx *.manifest pal_loader busybox

.PHONY: distclean
distclean: clean
	$(RM) -r $(SRCDIR)

