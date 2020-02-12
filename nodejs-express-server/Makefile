# List all the Node.js dependencies, besides Glibc libraries
.INTERMEDIATE: nodejs-deps
nodejs-deps:
        @ldd $(NODEJS_DIR)nodejs | \
                awk '{if ($$2 =="=>") {print $$1}}' | \
                sort | uniq | grep -v -x $(patsubst %,-e %,$(GLIBC_DEPS)) > $@

# Generate manifest rules for Node.js dependencies
.INTERMEDIATE: nodejs-trusted-libs
nodejs-trusted-libs: nodejs-deps
        @for F in `cat nodejs-deps`; do \
                P=`ldd $(NODEJS_DIR)nodejs | grep $$F | awk '{print $$3; exit}'`; \
                N=`echo $$F | tr --delete '.' | tr --delete '-' | tr --delete '+'`; \
                echo -n "sgx.trusted_files.$$N = file:$$P\\\\n"; \
        done > $@

nodejs.manifest: nodejs.manifest.template nodejs-trusted-libs
        @sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
                -e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
                -e 's|$$(NODEJS_DIR)|'"$(NODEJS_DIR)"'|g' \
                -e 's|$$(NODEJS_TRUSTED_LIBS)|'"`cat nodejs-trusted-libs`"'|g' \
                $< > $@

# Generate SGX-specific manifest, enclave signature, and token for enclave initialization
nodejs.manifest.sgx: nodejs.manifest
        $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
                -libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
                -key $(GRAPHENEKEY) \
                -manifest $< -output $@

nodejs.sig: nodejs.manifest.sgx

nodejs.token: nodejs.sig
        $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
                -output $@ -sig $^

# Extra executables
pal_loader:
        ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

.PHONY: clean
clean:
        $(RM) *.manifest *.manifest.sgx *.token *.sig pal_loader

.PHONY: distclean
distclean: clean

