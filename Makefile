PLATFORM ?=
TARGET ?= wheel

BUILD_ARGS = $(if $(PLATFORM),--platform=$(PLATFORM))
BUILD_ARGS += --tag libheif-binary:$(TARGET)
ifeq ($(TARGET),wheel)
BUILD_ARGS += --load --output type=local,dest=dist
endif

.PHONY: manylinux
manylinux:
	docker build $(BUILD_ARGS) -f Dockerfile.manylinux \
		--target $(TARGET) .
