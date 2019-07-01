# Build Memcached as follows:
#
# - make               -- create non-SGX no-debug-log manifest
# - make SGX=1         -- create SGX no-debug-log manifest
# - make SGX=1 DEBUG=1 -- create SGX debug-log manifest
#
# Any of these invokations clones Memcached git repository and builds Memcached
# in default configuration and of latest (master branch) version.
#
# Use `make clean` to remove Graphene-generated files and `make distclean` to
# additionally remove the cloned Memcached git repository.

# Relative path to Graphene root
GRAPHENEDIR = ../../../../..

SRCDIR = src
COMMIT = master

.PHONY=all
all: memcached memcached.manifest pal_loader
ifeq ($(SGX),1)
all: memcached.manifest.sgx
endif

ifeq ($(DEBUG),1)
GRAPHENEDEBUG = inline
else
GRAPHENEDEBUG = none
endif

$(SRCDIR)/configure:
	git clone --recursive https://github.com/memcached/memcached $(SRCDIR)
	cd $(SRCDIR) && git checkout $(COMMIT)
	cd $(SRCDIR) && ./autogen.sh

$(SRCDIR)/memcached: $(SRCDIR)/configure
	cd $(SRCDIR) && ./configure
	cd $(SRCDIR) && make

memcached.manifest: memcached.manifest.template
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		$< > $@

memcached.manifest.sgx: memcached.manifest $(SRCDIR)/memcached
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@ \
		-exec $(SRCDIR)/memcached
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output memcached.token -sig memcached.sig

memcached: $(SRCDIR)/memcached
	cp $< $@

pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

.PHONY=clean
clean:
	$(RM) *.token *.sig *.manifest.sgx *.manifest pal_loader memcached

.PHONY=distclean
distclean: clean
	$(RM) -r $(SRCDIR)
