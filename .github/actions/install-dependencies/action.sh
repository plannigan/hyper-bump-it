set -euo pipefail

echo "Ensuring pip is up to date"
python -m pip install --upgrade pip
message="Will install:\n"
install_args=""
if [[ "${INSTALL_REQUIREMENTS}" == "true"  ]]; then
  message="${message}- code requirements\n"
  install_args="${install_args} -r requirements.txt"
fi

if [[ "${INSTALL_TEST_REQUIREMENTS}" == "true"  ]]; then
  message="${message}- test requirements"
  install_args="${install_args} -r requirements-test.txt\n"
fi

if [[ "${INSTALL_DOCS_REQUIREMENTS}" == "true"  ]]; then
  message="${message}- docs requirements"
  install_args="${install_args} -r requirements-docs.txt\n"
fi

if [[ "${install_args}" == "" ]]; then
  echo "ERROR: No requirements to install"
  exit 1
fi

echo "${message}"
# shellcheck disable=SC2086
pip install ${install_args}

