set -euo pipefail

echo "Ensuring pip is up to date"
python -m pip install --upgrade pip
install_args=""
if [[ "${INSTALL_REQUIREMENTS}" == "true"  ]]; then
  echo "Installing code requirements"
  install_args="${install_args} -r requirements.txt"
  pip install -r requirements.txt
fi

if [[ "${INSTALL_TEST_REQUIREMENTS}" == "true"  ]]; then
  echo "Installing test requirements"
  install_args="${install_args} -r requirements-test.txt"
fi

if [[ "${install_args}" == "" ]]; then
  echo "ERROR: No requirements to install"
  exit 1
fi

# shellcheck disable=SC2086
pip install ${install_args}

