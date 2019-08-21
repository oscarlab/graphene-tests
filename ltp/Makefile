SRCDIR = src
BUILDDIR = opt/ltp
TESTCASEDIR = $(BUILDDIR)/testcases/bin
LTPSCENARIO = $(BUILDDIR)/runtest/syscalls

target = $(TESTCASEDIR)/pal_loader build-manifest
exec_target =

clean-extra = clean-build

level = ../../
include ../../Makefile

$(SRCDIR)/Makefile:
	$(error "$(SRCDIR) is empty. Please run `git submodule update --init $(SRCDIR)` or download the LTP source code (https://github.com/linux-test-project/ltp) into $(SRCDIR).")

$(SRCDIR)/configure: $(SRCDIR)/Makefile
	cd $(SRCDIR) && $(MAKE) autotools

$(BUILDDIR)/runltp: $(SRCDIR)/configure
	cd $(SRCDIR) && ./configure
	cd $(SRCDIR) && $(MAKE) all
	cd $(SRCDIR) && $(MAKE) "DESTDIR=$(PWD)" SKIP_IDCHECK=1 install

$(TESTCASEDIR)/pal_loader: $(BUILDDIR)/runltp
	ln -sf $(call relative-to,$(dir $@),../../../Runtime/pal_loader) $@

build-manifest: $(TESTCASEDIR)/manifest.template $(TESTCASEDIR)/Makefile
	cd $(TESTCASEDIR) && $(MAKE)

$(TESTCASEDIR)/manifest.template: manifest.template
	cp -f $< $@

$(TESTCASEDIR)/Makefile: Makefile.testcases
	ln -sf ../../../../$< $@

.PHONY: regression
regression:
	if test "$(SGX_RUN)" -eq 1; then \
		$(RM) ltp-sgx.xml; \
		$(MAKE) ltp-sgx.xml; \
	else \
		$(RM) ltp.xml; \
		$(MAKE) ltp.xml; \
	fi

%.xml: %.conf $(LTPSCENARIO) $(target)
	./conflint.py < $<
	./runltp_xml.py -c $< $(LTPSCENARIO) > $@

clean-build:
	cd $(SRCDIR) && $(MAKE) clean
	rm -rf $(BUILDDIR) ltp*.xml
