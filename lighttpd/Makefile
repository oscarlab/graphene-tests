# Build the manifest for Lighttpd:
#
# - make
# - make DEBUG=1
# - make SGX=1
# - make SGX=1 DEBUG=1
#
# Use `make clean` to remove Graphene-generated files.
#
# Use `make distclean` to further remove the Lighttpd tarball, source code,
# and installation.

# Constants

# Installation location of Lighttpd
INSTALL_DIR ?= install

# Source code directory and checksum of Lighttpd
LIGHTTPD_SRC ?= lighttpd-1.4.54
LIGHTTPD_CHECKSUM ?= 5151d38cb7c4c40effa13710e77ebdbef899f945b062cf32befc02d128ac424c

# Mirros for downloading the Lighttpd source code
LIGHTTPD_MIRRORS ?= \
	https://download.lighttpd.net/lighttpd/releases-1.4.x/

# Host and port for testing the Lighttpd server
HOST ?= 127.0.0.1
PORT ?= 8001
THREADS ?= 4
GRAPHENE_THREADS = 6

# Relative path to Graphene root
GRAPHENEDIR ?= ../../../../..

ifeq ($(DEBUG),1)
GRAPHENEDEBUG = inline
else
GRAPHENEDEBUG = none
endif

GREP = grep
SED  = sed
LDD  = ldd
AWK  = awk
RM   = rm

CONF_FILES = lighttpd-server.conf \
	     lighttpd.conf \
	     lighttpd-multithreaded.conf \
	     lighttpd-ssl.conf

.PHONY: all
all: $(INSTALL_DIR)/sbin/lighttpd lighttpd.manifest pal_loader $(CONF_FILES)
ifeq ($(SGX),1)
all: lighttpd.manifest.sgx
endif

# The commands for downloading and compiling the Lighttpd source code, and
# installing the binaries.
$(INSTALL_DIR)/sbin/lighttpd: $(LIGHTTPD_SRC)
	cd $(LIGHTTPD_SRC) && ./configure --prefix=$(abspath $(INSTALL_DIR)) \
		--with-openssl --without-pcre --without-zlib --without-bzip2
	cd $(LIGHTTPD_SRC) && $(MAKE)
	cd $(LIGHTTPD_SRC) && $(MAKE) install

$(LIGHTTPD_SRC): $(LIGHTTPD_SRC).tar.gz
	tar -xzf $<

$(LIGHTTPD_SRC).tar.gz:
	for MIRROR in $(LIGHTTPD_MIRRORS); do \
		wget --timeout=10 $${MIRROR}$(LIGHTTPD_SRC).tar.gz \
		&& break; \
	done

# Lighttpd dependencies (generate from ldd):
#
# For SGX, the manifest needs to list all the libraries loaded during the
# execution, so that the signer can include the file checksums.
#
# The dependencies are generated from the ldd results.

# Skip the GLIBC libraries because they are already listed
GLIBC_DEPS = linux-vdso /lib64/ld-linux-x86-64 libc libm librt libdl libpthread

LIGHTTPD_LIBS = $(INSTALL_DIR)/lib/mod_indexfile.so \
		$(INSTALL_DIR)/lib/mod_dirlisting.so \
		$(INSTALL_DIR)/lib/mod_staticfile.so

# Listing all the Lighttpd dependencies, besides Glibc libraries
.INTERMEDIATE: lighttpd-deps
lighttpd-deps:
	@$(LDD) $(LIGHTTPD_LIBS) $(INSTALL_DIR)/sbin/lighttpd | \
		$(AWK) '{if ($$2 =="=>") {split($$1,s,/\./); print s[1]}}' | \
		sort | uniq | $(GREP) -v -x $(patsubst %,-e %,$(GLIBC_DEPS)) > $@

# Generating manifest rules for Lighttpd dependencies
.INTERMEDIATE: lighttpd-trusted-libs
lighttpd-trusted-libs: lighttpd-deps
	@LIGHTTPD_LIBS="$(LIGHTTPD_LIBS)" && \
	for F in `cat lighttpd-deps`; do \
		P=`$(LDD) $$LIGHTTPD_LIBS $(INSTALL_DIR)/sbin/lighttpd | $(GREP) $$F | $(AWK) '{print $$3; exit}'`; \
		N=`echo $$F | tr --delete '-'`; \
		echo -n "sgx.trusted_files.$$N = file:$$P\\\\n"; \
	done > $@

.INTERMEDIATE: lighttpd-trusted-mods
lighttpd-trusted-mods:
	for F in $(LIGHTTPD_LIBS); do \
		N=`basename $$F .so | tr --delete '-'`; \
		echo -n "sgx.trusted_files.$$N = file:$$F\\\\n"; \
	done > $@

# Lighttpd manifests:
#   For each dependency, generate a rule as follows:
#       sgx.trusted_files.xxxx = file:xxxx

lighttpd.manifest: lighttpd.manifest.template lighttpd-trusted-libs lighttpd-trusted-mods
	$(SED) -e 's|$$(GRAPHENEDIR)|'"$(GRAPHENEDIR)"'|g' \
		-e 's|$$(GRAPHENEDEBUG)|'"$(GRAPHENEDEBUG)"'|g' \
		-e 's|$$(INSTALL_DIR)|'"$(INSTALL_DIR)"'|g' \
		-e 's|$$(INSTALL_DIR_ABSPATH)|'"$(abspath $(INSTALL_DIR))"'|g' \
		-e 's|$$(LIGHTTPD_TRUSTED_MODS)|'"`cat lighttpd-trusted-mods`"'|g' \
		-e 's|$$(LIGHTTPD_TRUSTED_LIBS)|'"`cat lighttpd-trusted-libs`"'|g' \
		-e 's|$$(THREADS)|'"$(GRAPHENE_THREADS)"'|g' \
		$< > $@

# Lighttpd manifests for SGX:
#   Generating the SGX-specific manifest (lighttpd.manifest.sgx), the enclave signature,
#   and the token for enclave initialization.

lighttpd.manifest.sgx: lighttpd.manifest
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-sign \
		-libpal $(GRAPHENEDIR)/Runtime/libpal-Linux-SGX.so \
		-key $(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/enclave-key.pem \
		-manifest $< -output $@
	$(GRAPHENEDIR)/Pal/src/host/Linux-SGX/signer/pal-sgx-get-token \
		-output lighttpd.token -sig lighttpd.sig

# Extra executables
pal_loader:
	ln -s $(GRAPHENEDIR)/Runtime/pal_loader $@

# Lighttpd configuration and test data
#

lighttpd-server.conf:
	@rm -rf $@
	@echo "server.document-root       = \"/html\""    >> $@
	@echo "server.port                = $(PORT)"            >> $@
	@echo "server.bind                = \"$(HOST)\""        >> $@

lighttpd.conf:
	@rm -rf $@
	@echo "include \"lighttpd-server.conf\""                >> $@
	@echo "include \"lighttpd-generic.conf\""               >> $@

lighttpd-multithreaded.conf:
	@rm -rf $@
	@echo "include \"lighttpd-server.conf\""                >> $@
	@echo "server.max-worker          = $(THREADS)"         >> $@
	@echo "include \"lighttpd-generic.conf\""               >> $@

lighttpd-ssl.conf: server.pem dhparam.pem
	@rm -rf $@
	@echo "include \"lighttpd-server.conf\""                >> $@
	@echo "include \"lighttpd-generic.conf\""               >> $@
	@echo ""                                                >> $@
	@echo "\$$SERVER[\"socket\"] == \"0.0.0.0:443\" {"      >> $@
	@echo "ssl.engine = \"enable\""                         >> $@
	@echo "ssl.pemfile = \"server.pem\""                    >> $@
	@echo "ssl.cipher-list = \"ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA\""	>> $@
	@echo "ssl.honor-cipher-order = \"enable\""             >> $@
	@echo "ssl.dh-file = \"dhparam.pem\""                   >> $@
	@echo "ssl.ec-curve = \"secp384r1\""                    >> $@
	@echo "}"                                               >> $@

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

.PHONY: testdata
testdata: $(TEST_DATA)

$(RANDOM_DIR)/%.html:
	mkdir -p $(RANDOM_DIR)
	dd if=/dev/urandom of=$@ count=1 bs=$(basename $(basename $(notdir $@)))

# Commands for running Lighttpd
#
# - make start-native-server:
#     Start the Lighttpd server natively in the foreground (using the Prefork MPM)
#
# - make start-graphene-server:
#     Start the Lighttpd server under Graphene in the foreground (using the Prefork MPM)
#
# - make start-native-multithreaded-server:
#     Start the Lighttpd server natively in the foreground (using the Worker MPM)
#
# - make start-graphene-multithreaded-server:
#     Start the Lighttpd server under Graphene in the foreground (using the Worker MPM)
#
# - make start-native-ssl-server:
#     Start the Lighttpd HTTPS server natively in the foreground (using the Worker MPM)
#
# - make start-graphene-ssl-server:
#     Start the Lighttpd HTTPS server under Graphene in the foreground (using the Worker MPM)

.PHONY: start-native-server
start-native-server: | testdata
	$(INSTALL_DIR)/sbin/lighttpd -D -m $(INSTALL_DIR)/lib -f lighttpd.conf

.PHONY: start-native-multithreaded-server
start-native-multithreaded-server: | testdata
	$(INSTALL_DIR)/sbin/lighttpd -D -m $(INSTALL_DIR)/lib -f lighttpd-multithreaded.conf

.PHONY: start-native-ssl-server
start-native-ssl-server: | testdata
	$(INSTALL_DIR)/sbin/lighttpd -D -m $(INSTALL_DIR)/lib -f lighttpd-ssl.conf

.PHONY: start-graphene-server
start-graphene-server: | testdata
	./pal_loader lighttpd.manifest -D -m $(INSTALL_DIR)/lib -f lighttpd.conf

.PHONY: start-graphene-multithreaded-server
start-graphene-multithreaded-server: | testdata
	./pal_loader lighttpd.manifest -D -m $(INSTALL_DIR)/lib -f lighttpd-multithreaded.conf

.PHONY: start-graphene-ssl-server
start-graphene-ssl-server: | testdata
	./pal_loader lighttpd.manifest -D -m $(INSTALL_DIR)/lib -f lighttpd-ssl.conf

.PHONY: clean
clean:
	$(RM) -f *.manifest *.manifest.sgx *.token *.sig pal_loader $(CONF_FILES) pal_loader

.PHONY: distclean
distclean: clean
	$(RM) -rf $(LIGHTTPD_SRC).tar.gz $(LIGHTTPD_SRC) $(INSTALL_DIR) $(TEST_DATA) *.pem
