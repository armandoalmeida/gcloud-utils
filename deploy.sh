#!/usr/bin/env bash

rm -rf build dist simple_gcp_utils.egg-info
python3 setup.py sdist bdist_wheel
twine upload dist/*