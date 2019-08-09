import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="simple-gcp",
    version="1.0.1",
    description="Google Cloud Utilities for Python 3",
    long_description=README,
    long_description_content_type="text/markdown",
    url="http://gitlab.ingaia.com.br/jose.almeida/chargebee-operations-api",
    author="Jose Armando de Almeida Neto",
    author_email="jose@armandoalmeida.com.br",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["gcputils"],
    include_package_data=False,
    install_requires=["google-cloud-firestore", "google-cloud-datastore", "google-cloud-tasks", "google-cloud-storage",
                      "google-cloud-bigquery"],
    entry_points={
        "console_scripts": [
            "simple-gcp=gcputils.__main__:main",
        ]
    },
)
