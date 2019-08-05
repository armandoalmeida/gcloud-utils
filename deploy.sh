#!/usr/bin/env bash

# Example: ./deploy.sh 1.0.1 patch

rm -rf build dist simple_gcp_utils.egg-info
bumpversion --current-version $1 $2 setup.py gcputils/__init__.py --allow-dirt
python3 setup.py sdist bdist_wheel
twine upload dist/*