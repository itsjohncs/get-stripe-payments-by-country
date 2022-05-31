#!/usr/bin/env bash

set -eu

if [[ ! $VIRTUAL_ENV =~ get-stripe-payments-by-country ]]; then
    echo "FATAL: venv not active"
    exit 1
fi

ROOT_DIR="$(realpath --relative-to="$PWD" "$(dirname "${BASH_SOURCE[0]}")")"

mapfile -d "" -t PYTHON_FILES < <(
    find "$ROOT_DIR/src" -name "*.py" -print0
)
SHELL_FILES=("$ROOT_DIR"/*.sh)

set -x

shfmt -i=4 -sr -w "${SHELL_FILES[@]}"

black --line-length 80 "${PYTHON_FILES[@]}"
