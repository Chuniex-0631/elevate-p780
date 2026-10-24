#!/bin/sh
set -eu
cd "$(dirname "$0")"
"${CC:-aarch64-linux-gnu-gcc}" -O2 -Wall -Wextra -Werror -static -Wl,--build-id=none \
  perf_permission.c -o p780-perf-permission-arm64
