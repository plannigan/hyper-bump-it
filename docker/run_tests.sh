#!/usr/bin/env bash

set -eo pipefail

BLACK_ACTION="--check"
ISORT_ACTION="--check-only"

function usage
{
    echo "usage: run_tests.sh [--format-code]"
    echo ""
    echo " --format-code : Format the code instead of checking formatting."
    exit 1
}

while [[ $# -gt 0 ]]; do
    arg="$1"
    case $arg in
        --format-code)
        BLACK_ACTION="--quiet"
        ISORT_ACTION=""
        ;;
        -h|--help)
        usage
        ;;
        "")
        # ignore
        ;;
        *)
        echo "Unexpected argument: ${arg}"
        usage
        ;;
    esac
    shift
done

echo "Running black..."
black ${BLACK_ACTION} .

echo "Running iSort..."
# shellcheck disable=SC2086
isort ${ISORT_ACTION} .

echo "Running MyPy..."
mypy

echo "Running pytest..."
# only generate html locally
pytest --cov-report html

echo "Running flake8..."
flake8

echo "Running bandit..."
bandit --ini .bandit --quiet -r .
