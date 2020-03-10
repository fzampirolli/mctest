# IN_FILES = espalhador.py interpreter.py linker_script.sh vpl_evaluate.cpp vpl_execution.sh vpl_runsh
IN_FILES = ./*

COMMAND_TAR = tar
COMMAND_GZ = gzip
COMMAND_B64 = base64

TAG_ZIP_TAR = -cf
TAG_ZIP_GZ = -c --best
TAG_ZIP_B64 =

TAG_UNZIP_TAR = -xf
TAG_UNZIP_GZ = -d
TAG_UNZIP_B64 = -d

OUT_FILE = ./zip

OUT_FILE_TAR = $(OUT_FILE).tar
OUT_FILE_GZ = $(OUT_FILE_TAR).gz
OUT_FILE_B64 = $(OUT_FILE_GZ).b64

################################################################################

unzip: .unzip_tar
	@#

zip: .zip_tar_gz_b64
	@#

################################################################################

.unzip_tar: .unzip_tar_gz $(OUT_FILE_TAR)
	@$(COMMAND_TAR) $(TAG_UNZIP_TAR) $(OUT_FILE_TAR); \
	rm $(OUT_FILE_TAR)

.unzip_tar_gz: .unzip_tar_gz_b64 $(OUT_FILE_GZ)
	@$(COMMAND_GZ) $(TAG_UNZIP_GZ) $(OUT_FILE_GZ)

.unzip_tar_gz_b64: $(OUT_FILE_B64)
	@$(COMMAND_B64) $(TAG_UNZIP_B64) $(OUT_FILE_B64) > $(OUT_FILE_GZ); \
	rm $(OUT_FILE_B64)

################################################################################

.zip_tar_gz_b64: .clear_zip_tar_gz_b64 .zip_tar_gz
	@$(COMMAND_B64) $(TAG_ZIP_B64) $(OUT_FILE_GZ) > $(OUT_FILE_B64) ; \
	rm $(OUT_FILE_GZ)

.zip_tar_gz: .zip_tar .clear_zip_tar_gz
	@$(COMMAND_GZ) $(TAG_ZIP_GZ) $(OUT_FILE_TAR) > $(OUT_FILE_GZ) ; \
	rm $(OUT_FILE_TAR)

.zip_tar: .clear_zip_tar $(IN_FILES)
	@$(COMMAND_TAR) $(TAG_ZIP_TAR) $(OUT_FILE_TAR) $(IN_FILES)

################################################################################

clear: .clear_zip_tar_gz_b64 .clear_zip_tar_gz .clear_zip_tar
	@#

################################################################################

.clear_zip_tar_gz_b64:
	@if [ -e $(OUT_FILE_B64) ] ; then \
		rm $(OUT_FILE_B64); \
	fi

.clear_zip_tar_gz:
	@if [ -e $(OUT_FILE_GZ) ] ; then \
		rm $(OUT_FILE_GZ); \
	fi

.clear_zip_tar: 
	@if [ -e $(OUT_FILE_TAR) ] ; then \
		rm $(OUT_FILE_TAR); \
	fi
