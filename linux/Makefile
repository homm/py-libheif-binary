BASE ?= manylinux
PLATFORM ?=
TARGET ?= wheel

BUILD_ARGS = $(if $(PLATFORM),--platform=$(PLATFORM))
BUILD_ARGS += --build-arg BASE=$(BASE) --tag libheif-binary:$(BASE)-$(TARGET)
ifeq ($(TARGET),wheel)
BUILD_ARGS += --load --output type=local,dest=../dist
endif

.PHONY: manylinux musllinux
musllinux: BASE = musllinux
manylinux musllinux:
	docker build $(BUILD_ARGS) -f Dockerfile \
		--target $(TARGET) ..
