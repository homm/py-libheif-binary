BASE ?= manylinux
ARCH ?=
TARGET ?= wheel

BUILD_ARGS = $(if $(ARCH),--platform=linux/$(ARCH))
BUILD_ARGS += --build-arg BASE=$(BASE) --tag libheif-binary:$(BASE)-$(TARGET)
ifeq ($(TARGET),wheel)
BUILD_ARGS += --load --output type=local,dest=../dist
endif

.PHONY: manylinux musllinux
musllinux: BASE = musllinux
manylinux musllinux:
	docker build $(BUILD_ARGS) -f Dockerfile \
		--target $(TARGET) ..
