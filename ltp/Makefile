SRCDIR = src
BUILDDIR = opt/ltp
TESTCASEDIR = $(BUILDDIR)/testcases/bin

target = $(BUILDDIR)/bin/run_in_graphene.awk $(TESTCASEDIR)/pal_loader build-manifest
exec_target =

clean-extra = clean-build

include ../../Makefile.Test

$(SRCDIR)/Makefile:
	$(error "$(SRCDIR) is empty. Please run `git submodule update --init $(SRCDIR)` or download the LTP source code (https://github.com/linux-test-project/ltp) into $(SRCDIR).")

$(SRCDIR)/configure: $(SRCDIR)/Makefile
	cd $(SRCDIR) && $(MAKE) autotools

$(BUILDDIR)/runltp: $(SRCDIR)/configure
	cd $(SRCDIR) && ./configure
	cd $(SRCDIR) && $(MAKE) all
	cd $(SRCDIR) && $(MAKE) "DESTDIR=$(PWD)" SKIP_IDCHECK=1 install
	patch -d $(dir $@) < runltp.patch

$(BUILDDIR)/bin/run_in_graphene.awk: run_in_graphene.awk $(BUILDDIR)/runltp
	cp -f $< $@

$(TESTCASEDIR)/pal_loader: $(BUILDDIR)/runltp
	ln -sf $(call relative-to,$(dir $@),../../../Runtime/pal_loader) $@

build-manifest: $(TESTCASEDIR)/manifest.template $(TESTCASEDIR)/Makefile
	cd $(TESTCASEDIR) && $(MAKE)

$(TESTCASEDIR)/manifest.template: manifest.template
	cp -f $< $@

$(TESTCASEDIR)/Makefile: Makefile.testcases
	ln -sf ../../../../$< $@

regression:
	@echo "\n\nBuilding LTP..."
	@$(MAKE) >> /dev/null 2>&1

	@echo "\n\nLTP tests for system calls:"
	./syscalls.sh

.PHONY: sgx-tokens
sgx-tokens: build-manifest
	$(MAKE) -C $(TESTCASEDIR) $@

clean-build:
	cd $(SRCDIR) && $(MAKE) clean
	rm -rf $(BUILDDIR) *.csv opt run_output syscalls.graphene
