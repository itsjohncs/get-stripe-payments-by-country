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

RV=0

if ! shfmt -i=4 -sr -d "${SHELL_FILES[@]}"; then
    RV=1
fi

if ! shellcheck "${SHELL_FILES[@]}"; then
    RV=1
fi

if ! pylint --disable=C0103,C0114,C0116,C0115,R1705,R0911 "${PYTHON_FILES[@]}"; then
    RV=1
fi

if ! black --line-length 80 --check "${PYTHON_FILES[@]}"; then
    RV=1
fi

exit $RV
