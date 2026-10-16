SHELL := /bin/bash

UPDATE_FILES := libheif.env x265.env de265.env aom.env webp.env libpng.env libjpeg.env

.PHONY: update FORCE
update: $(UPDATE_FILES)

FORCE:

$(UPDATE_FILES): PREFIX = $(shell printf '%s' '$*' | tr '[:lower:]' '[:upper:]')

libheif.env: REPOSITORY = strukturag/libheif
de265.env: REPOSITORY = strukturag/libde265
aom.env: TAGS_URL = https://aomedia.googlesource.com/aom/+refs/tags?format=JSON
webp.env: TAGS_URL = https://chromium.googlesource.com/webm/libwebp/+refs/tags?format=JSON
libpng.env: REPOSITORY = pnggroup/libpng
libjpeg.env: REPOSITORY = libjpeg-turbo/libjpeg-turbo

$(UPDATE_FILES): DISCOVER = gh api --paginate 'repos/$(REPOSITORY)/releases?per_page=100' \
	--jq '.[] | select(.draft == false and .prerelease == false) | .tag_name'
libpng.env: DISCOVER = gh api --paginate 'repos/$(REPOSITORY)/tags?per_page=100' --jq '.[].name'
aom.env webp.env: DISCOVER = curl -fsSL '$(TAGS_URL)' | sed '1d' | jq -r 'keys[]'
x265.env: DISCOVER = set -e; \
	next='https://api.bitbucket.org/2.0/repositories/multicoreware/x265_git/downloads?pagelen=100'; \
	while [ -n "$$next" ]; do \
		page=$$(curl -fsSL "$$next"); \
		jq -r '.values[].name | capture("^x265_(?<version>[0-9]+\\.[0-9]+(\\.[0-9]+)?)\\.tar\\.gz$$").version' <<< "$$page"; \
		next=$$(jq -r '.next // empty' <<< "$$page"); \
	done

$(UPDATE_FILES): %.env: FORCE
	@set -euo pipefail; \
	trap 'printf "Failed to update %s: %s\n" "$@" "$$BASH_COMMAND" >&2' ERR; \
	versions=$$($(DISCOVER)); \
	current=$$(sed -n 's/^$(PREFIX)_VERSION=//p' "$@"); \
	latest=$$(printf '%s\n' "$$versions" | jq -Rser --arg current "$$current" '\
		def version: split(".") | map(tonumber) | . + [0] | .[0:3]; \
		[split("\n")[] | sub("^refs/tags/"; "") | sub("^v"; "") \
		| select(test("^[0-9]+\\.[0-9]+(\\.[0-9]+)?$$"))] \
		| if length == 0 then error("no stable versions found") \
		else max_by(version) | if version > ($$current | version) then . else "" end end'); \
	if [ -z "$$latest" ]; then \
		printf '%s: already at %s or newer\n' '$*' "$$current"; \
		exit 0; \
	fi; \
	url=$$(sed -n 's/^$(PREFIX)_URL=//p' "$@"); \
	placeholder='$${$(PREFIX)_VERSION}'; \
	url="$${url//$$placeholder/$$latest}"; \
	archive=$$(mktemp "$${TMPDIR:-/tmp}/libheif-update.XXXXXXXX"); \
	trap 'rm -f "$$archive"' EXIT; \
	curl -fsSL "$$url" -o "$$archive"; \
	tar -tzf "$$archive" >/dev/null; \
	checksum=$$(shasum -a 256 "$$archive" | cut -d ' ' -f1); \
	updated=$$(sed \
		-e "s/^$(PREFIX)_VERSION=.*/$(PREFIX)_VERSION=$$latest/" \
		-e "s/^$(PREFIX)_SHA256=.*/$(PREFIX)_SHA256=$$checksum/" "$@"); \
	printf '%s\n' "$$updated" > "$@"; \
	printf '### %s: %s → %s\nSource: %s\nSHA-256: %s\n\n' \
		'$*' "$$current" "$$latest" "$$url" "$$checksum"

# Discover upstream HEAD from VideoLAN because the GitHub mirror's branches are stale; keep GitHub for archive downloads.
x264.env: DISCOVER = curl -fsSL 'https://code.videolan.org/api/v4/projects/videolan%2Fx264/repository/commits/master' | jq -r .id
x264.env: FORCE
	@set -euo pipefail; \
	trap 'printf "Failed to update %s: %s\n" "$@" "$$BASH_COMMAND" >&2' ERR; \
	latest=$$($(DISCOVER)); \
	current=$$(sed -n 's/^X264_COMMIT=//p' "$@"); \
	if [ "$$latest" = "$$current" ]; then \
		printf 'x264: already at %s\n' "$$current"; \
		exit 0; \
	fi; \
	url=$$(sed -n 's/^X264_URL=//p' "$@"); \
	placeholder='$${X264_COMMIT}'; \
	url="$${url//$$placeholder/$$latest}"; \
	archive=$$(mktemp "$${TMPDIR:-/tmp}/libheif-update.XXXXXXXX"); \
	trap 'rm -f "$$archive"' EXIT; \
	curl -fsSL "$$url" -o "$$archive"; \
	build=$$(tar -xOf "$$archive" "x264-$$latest/x264.h" \
		| sed -n 's/^#define X264_BUILD \([0-9][0-9]*\)$$/\1/p'); \
	test -n "$$build"; \
	checksum=$$(shasum -a 256 "$$archive" | cut -d ' ' -f1); \
	updated=$$(sed \
		-e "s/^X264_COMMIT=.*/X264_COMMIT=$$latest/" \
		-e "s/^X264_SHA256=.*/X264_SHA256=$$checksum/" \
		-e "s/^X264_BUILD=.*/X264_BUILD=$$build/" "$@"); \
	printf '%s\n' "$$updated" > "$@"; \
	printf '### x264: %s → %s\nBuild: %s\nSource: %s\nSHA-256: %s\n\n' \
		"$$current" "$$latest" "$$build" "$$url" "$$checksum"
