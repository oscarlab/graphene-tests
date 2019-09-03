# Build the manifest for lighttpd:
#
# - make                Building for Linux
# - make DEBUG=1        Building for Linux (with Graphene debug output)
# - make SGX=1          Building for SGX
# - make SGX=1 DEBUG=1  Building for SGX (with Graphene debug output)
#
# Use `make clean` to remove Graphene-generated files.
#
# Use `make distclean` to further remove the lighttpd tarball, source code,
# and installation.

# Constants

# Installation and source code of lighttpd
INSTALL_DIR ?= install
LIGHTTPD_SRC ?= lighttpd-1.4.54
LIGHTTPD_CHECKSUM ?= 5151d38cb7c4c40effa13710e77ebdbef899f945b062cf32befc02d128ac424c

# Mirros for downloading the lighttpd source code
LIGHTTPD_MIRRORS ?= \
	https://download.lighttpd.net/lighttpd/releases-1.4.x/

# Address and port that the lighttpd server listens to
LISTEN_HOST ?= 127.0.0.1
LISTEN_PORT ?= 8001

# Number of lighttpd threads for multithreaded execution
LIGHTTPD_THREADS ?= 25

# Relative path to Graphene root
GRAPHENEDIR ?= ../../../../..

ifeq ($(DEBUG),1)
GRAPHENEDEBUG = inline
else
GRAPHENEDEBUG = none
endif

CONF_FILES = lighttpd-server.conf \
	     lighttpd.conf \
	     lighttpd-multithreaded.conf \
	     lighttpd-ssl.conf

.PHONY: all
all: $(INSTALL_DIR)/sbin/lighttpd lighttpd.manifest pal_loader config testdata
ifeq ($(SGX),1)
all: lighttpd.manifest.sgx lighttpd.sig lighttpd.token
endif

# The commands for downloading and compiling the lighttpd source code, and
# installing the binaries.
$(INSTALL_DIR)/sbin/lighttpd: $(LIGHTTPD_SRC)/configure
	cd $(LIGHTTPD_SRC) && ./configure --prefix=$(abspath $(INSTALL_DIR)) \
		--with-openssl --without-pcre --without-zlib --without-bzip2
	cd $(LIGHTTPD_SRC) && $(MAKE)
	cd $(LIGHTTPD_SRC) && $(MAKE) install

$(LIGHTTPD_SRC)/configure: $(LIGHTTPD_SRC).tar.gz
	tar -xzf $<
	[ -f $@ ] && touch $@

$(LIGHTTPD_SRC).tar.gz:
	for MIRROR in $(LIGHTTPD_MIRRORS); do \
		wget --timeout=10 $${MIRROR}$(LIGHTTPD_SRC).tar.gz -O tmp \
		&& break; \
	done
	@[ "`sha256sum tmp`" = "$(LIGHTTPD_CHECKSUM)  tmp" ] || \
		(echo "*** $@ has a wrong checksum ***"; rm -f tmp; exit 255)
	mv -f tmp $@

# lighttpd dependencies (generate from ldd):
#
# For SGX, the manifest needs to list all the libraries loaded during the
# execution, so that the signer can include the file checksums.
#
# The dependencies are generated from the ldd results.

# We need to replace Glibc dependencies with Graphene-specific Glibc. The Glibc
# binaries are already listed in the manifest template, so we can skip them
# from the ldd results
GLIBC_DEPS = linux-vdso /lib64/ld-linux-x86-64 libc libm librt libdl libpthread

LIGHTTPD_LIBS = $(INSTALL_DIR)/sbin/lighttpd \
		$(INSTALL_DIR)/lib/mod_indexfile.so \
		$(INSTALL_DIR)/lib/mod_dirlisting.so \
		$(INSTALL_DIR)/lib/mod_staticfile.so \
		$(INSTALL_DIR)/lib/mod_access.so \
		$(INSTALL_DIR)/lib/mod_alias.so \
		$(INSTALL_DIR)/lib/mod_openssl.so

# Listing all the lighttpd dependencies, besides Glibc libraries
.INTERMEDIATE: lighttpd-deps
lighttpd-deps:
	@ldd $(LIGHTTPD_LIBS) | \
		awk '{if ($$2 =="=>") {split($$1,s,/\./); print s[1]}}' | \
		sort | uniq | grep -v -x $(patsubst %,-e %,$(GLIBC_DEPS)) > $@

# Generating manifest rules for lighttpd dependencies
.INTERMEDIATE: lighttpd-trusted-libs
lighttpd-trusted-libs: lighttpd-deps
	@LIGHTTPD_LIBS="$(LIGHTTPD_LIBS)" && \
	for F in `cat lighttpd-deps`; do \
		P=`ldd $$LIGHTTPD_LIBS | grep $$F | awk '{print $$3; exit}'`; \
		N=`echo $$F | tr --delete '-'`; \
		echo -n "sgx.trusted_files.$$N = file:$$P\\\\n"; \
	done > $@

# lighttpd manifests:
#   For each dependency, generate a rule as follows:
#       sgx.trusted_files.xxxx = file:xxxx

lighttpd.manifest: lighttpd.manifest.template lighttpd-trusted-libs
	sed -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		-e 's|$$(PWD)|'"$(PWD)"'|g' \
		-e 's|$$(INSTALL_DIR)|'"$(INSTALL_DIR)"'|g' \
		-e 's|$$(LIGHTTPD_TRUSTED_LIBS)|'"`cat lighttpd-trusted-libs`"'|g' \
		$< > $@

# lighttpd manifests for SGX:
#   Generating the SGX-specific manifest (lighttpd.manifest.sgx), the enclave signature,
#   and the token for enclave initialization.

lighttpd.manifest.sgx: lighttpd.manifest
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@

lighttpd.sig: lighttpd.manifest.sgx

lighttpd.token: lighttpd.sig
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output lighttpd.token -sig lighttpd.sig

# Extra executables
pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

# lighttpd configuration and test data

.PHONY: config
config: $(CONF_FILES)

lighttpd-server.conf:
	@rm -rf $@
	@echo "server.document-root = \"$(PWD)/html\""          >> $@
	@echo "server.port = $(LISTEN_PORT)"                    >> $@
	@echo "server.bind = \"$(LISTEN_HOST)\""                >> $@

lighttpd.conf:
	@rm -rf $@
	@echo "include \"lighttpd-server.conf\""                >> $@
	@echo "include \"lighttpd-generic.conf\""               >> $@

lighttpd-multithreaded.conf:
	@rm -rf $@
	@echo "include \"lighttpd-server.conf\""                >> $@
	@echo "server.max-worker = $(LIGHTTPD_THREADS)"         >> $@
	@echo "include \"lighttpd-generic.conf\""               >> $@

lighttpd-ssl.conf: server.pem dhparam.pem
	@rm -rf $@
	@echo "include \"lighttpd-server.conf\""                >> $@
	@echo "include \"lighttpd-generic.conf\""               >> $@
	@echo "ssl.engine = \"enable\""                         >> $@
	@echo "ssl.pemfile = \"server.pem\""                    >> $@
	@echo "ssl.dh-file = \"dhparam.pem\""                   >> $@

server.pem:
	openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes -subj "/cn=lighttpd/o=oscar/dc=cs/dc=stonybrook/dc=edu/"

dhparam.pem:
	openssl dhparam -out dhparam.pem 2048

# HTTP docs:
# Generating random HTML files in html/random

RANDOM_DIR = html/random
RANDOM_FILES = \
	$(foreach n,1 2 3 4 5 6 7 8 9 10,2K.$n.html) \
	$(foreach n,1 2 3 4 5,10K.$n.html) \
	$(foreach n,1 2 3 4 5,100K.$n.html) \
	$(foreach n,1 2 3,1M.$n.html) \
	$(foreach n,1 2 3,10M.$n.html) \
	$(foreach n,1 2 3,100.$n.html)

TEST_DATA = $(addprefix $(RANDOM_DIR)/,$(RANDOM_FILES))

$(RANDOM_DIR)/%.html:
	mkdir -p $(RANDOM_DIR)
	dd if=/dev/urandom of=$@ count=1 bs=$(basename $(basename $(notdir $@)))

.PHONY: testdata
testdata: $(TEST_DATA)

# Commands for running lighttpd
#
# - make start-native-server:
#     Start the lighttpd server natively in the foreground (single-threaded)
#
# - make start-graphene-server:
#     Start the lighttpd server under Graphene in the foreground (single-thread)
#
# - make start-native-multithreaded-server:
#     Start the lighttpd server natively in the foreground (multi-threaded)
#
# - make start-graphene-multithreaded-server:
#     Start the lighttpd server under Graphene in the foreground (multi-threaded)
#
# - make start-native-ssl-server:
#     Start the lighttpd HTTPS server natively in the foreground (single-threaded)
#
# - make start-graphene-ssl-server:
#     Start the lighttpd HTTPS server under Graphene in the foreground (single-threaded)

.PHONY: start-native-server
start-native-server: all
	$(INSTALL_DIR)/sbin/lighttpd -D -m $(INSTALL_DIR)/lib -f lighttpd.conf

.PHONY: start-native-multithreaded-server
start-native-multithreaded-server: all
	$(INSTALL_DIR)/sbin/lighttpd -D -m $(INSTALL_DIR)/lib -f lighttpd-multithreaded.conf

.PHONY: start-native-ssl-server
start-native-ssl-server: all
	$(INSTALL_DIR)/sbin/lighttpd -D -m $(INSTALL_DIR)/lib -f lighttpd-ssl.conf

.PHONY: start-graphene-server
start-graphene-server: all
	./pal_loader lighttpd.manifest -D -m $(INSTALL_DIR)/lib -f lighttpd.conf

.PHONY: start-graphene-multithreaded-server
start-graphene-multithreaded-server: all
	./pal_loader lighttpd.manifest -D -m $(INSTALL_DIR)/lib -f lighttpd-multithreaded.conf

.PHONY: start-graphene-ssl-server
start-graphene-ssl-server: all
	./pal_loader lighttpd.manifest -D -m $(INSTALL_DIR)/lib -f lighttpd-ssl.conf

.PHONY: clean
clean:
	rm -f *.manifest *.manifest.sgx *.token *.sig pal_loader $(CONF_FILES) *.pem pal_loader OUTPUT result-* *.html*

.PHONY: distclean
distclean: clean
	rm -rf $(LIGHTTPD_SRC).tar.gz $(LIGHTTPD_SRC) $(INSTALL_DIR) $(TEST_DATA)
