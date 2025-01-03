set -euo pipefail

echo "Ensuring pip is up to date"
python -m pip install --upgrade pip==24.3.1
echo "Installing the latest version of pypa/build"
pip install build==1.2.2.post1

python -m build .
