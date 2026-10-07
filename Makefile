SHELL := /bin/bash

.PHONY: collect_dist
collect_dist:
	@set -euo pipefail; \
	sha=$$(git rev-parse HEAD); \
	printf 'Downloading dists for %s\n' "$$(git log -1 --format='%h %s')"; \
	mkdir -p dist; \
	gh api --paginate 'repos/{owner}/{repo}/actions/artifacts?per_page=100' \
		--jq ".artifacts[] | select(.workflow_run.head_sha == \"$$sha\") | [.id, .name, .size_in_bytes] | @tsv" | \
	while IFS=$$'\t' read -r artifact name size; do \
		case "$$name" in \
			*-manylinux_*.whl|*-musllinux_*.whl|*_universal2.whl) ;; \
			*) continue ;; \
		esac; \
		if [ -e "dist/$$name" ]; then \
			if [ "$$(wc -c < "dist/$$name")" -ne "$$size" ]; then \
				printf 'stopped (size mismatch): %s\n' "$$name" >&2; \
				exit 1; \
			fi; \
			printf 'skipped (already exists): %s\n' "$$name"; \
			continue; \
		fi; \
		temporary=$$(mktemp dist/.collect_dist.XXXXXX); \
		trap 'rm -f "$$temporary"' EXIT; \
		gh api "repos/{owner}/{repo}/actions/artifacts/$$artifact/zip" > "$$temporary"; \
		if [ "$$(wc -c < "$$temporary")" -ne "$$size" ]; then \
			printf 'stopped (downloaded file size mismatch): %s\n' "$$name" >&2; \
			exit 1; \
		fi; \
		mv "$$temporary" "dist/$$name"; \
		trap - EXIT; \
		printf 'downloaded: %s\n' "$$name"; \
	done
