GRAPHENEDIR?=../../../../..

ifeq ($(DEBUG),1)
GRAPHENEDEBUG = inline
else
GRAPHENEDEBUG = none
endif

DISTRIB_ID ?= $(shell grep _ID /etc/lsb-release | cut -d= -f2)
DISTRIB_RLEASE_MAJOR ?= $(shell grep _RELEASE /etc/lsb-release | cut -d= -f 2 | cut -d. -f 1)

ifneq ($(DISTRIB_ID),Ubuntu)
$(error This example requires Ubuntu.)
endif

UBUNTU_VERSION = $(DISTRIB_ID)$(DISTRIB_RLEASE_MAJOR)

.PHONY: default
default: pytorch.token python3.token

pytorch.sig: python3.sig

# .manifest.template contains stanzas for both Ubuntu 16 and 18. The last rule selectively enables
# those lines based on the Ubuntu version detected.
%.manifest: %.manifest.template
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		-e 's|$$(HOME)|'"$(HOME)"'|g' \
	    -e 's|# '"$(UBUNTU_VERSION)"' ||g' \
		$< > $@

pytorch.sig: pytorch.manifest
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign -libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so -key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem -output pytorch.manifest.sgx -exec /usr/bin/python3 -manifest $<

%.token: %.sig
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token -output $@ -sig $<

# The PyTorch workload forks/execve()s at some point. This rule generates the required additional
# manifest for the child process.
python3.manifest: pytorch.manifest
	cp $< $@
	sed -i '/trusted_children/d' $@

python3.sig: python3.manifest
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign -libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so -key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem -output python3.manifest.sgx -exec /usr/bin/python3 -manifest $<

.PHONY: clean
clean:
	$(RM) $(addprefix pytorch., token sig manifest manifest.sgx)
	$(RM) $(addprefix python3., token sig manifest manifest.sgx)
