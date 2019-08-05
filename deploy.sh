#!/usr/bin/env bash

rm -rf build dist simple_gcp_utils.egg-info
bumpversion --current-version $1 $2 setup.py gcputils/__init__.py --allow-dirt
python3 setup.py sdist bdist_wheel
twine upload dist/*