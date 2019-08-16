manifests = curl.manifest

target =
exec_target = $(manifests)

clean-extra += clean-tmp

include ../../Makefile.Test

clean-tmp:
	rm -f curl.manifest.sgx
