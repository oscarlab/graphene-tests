GRAPHENEDIR = $(abspath ../../../../..)

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

$(SRCDIR):
	git clone --recursive https://github.com/microsoft/LightGBM $(SRCDIR)
	cd $(SRCDIR) && git checkout $(COMMIT)
	cd $(SRCDIR) && mkdir -p build
	cd $(SRCDIR)/build && cmake ..

$(SRCDIR)/lightgbm: $(SRCDIR)
	cd $(SRCDIR)/build && make

lightgbm.manifest: lightgbm.manifest.template
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
	    -e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
        -e 's|$$(PALLOADER)|'"$(abspath $(GRAPHENEDIR)/Runtime/pal_loader)"'|g' \
	    $< > $@
	    chmod ugo+x $@

lightgbm.manifest.sgx: lightgbm.manifest $(SRCDIR)/lightgbm
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@ \
		-exec $(SRCDIR)/lightgbm
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output lightgbm.token -sig lightgbm.sig

lightgbm: $(SRCDIR)/lightgbm 
	cp -p $(SRCDIR)/lightgbm lightgbm
	cp -prf $(SRCDIR)/examples/ examples/

pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@


.PHONY=clean
clean:
	$(RM) *.token *.sig *.manifest.sgx *.manifest pal_loader lightgbm

.PHONY=distclean
distclean: clean
	$(RM) -r $(SRCDIR)



