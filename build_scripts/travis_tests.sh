#!/bin/bash

set -e
set -u

echo "Running setup.py install"
python setup.py install

echo "Running tests that don't need Clair"
pytest tests/ -v -m "not needs_clair" --cov clair_singularity --cov-report term-missing

if [[ $TRAVIS_PYTHON_VERSION == "3.6"* ]]; then
    echo "Python 3.6 - running docker tests with Clair"
    docker pull arminc/clair-db:2021-06-14
    docker run -d --name clair-db arminc/clair-db:2021-06-14
    sleep 5
    docker pull arminc/clair-local-scan:v2.1.7_5125fde67edee46cb058a3feee7164af9645e07d
    docker run -p 6060:6060 --link clair-db:postgres -d --name clair arminc/clair-local-scan:v2.1.7_5125fde67edee46cb058a3feee7164af9645e07d
    docker ps
    docker build -t clair-singularity .

    # Clear out any old .pyc from the local tests
    find . -name *.pyc -delete

    docker run -v $TRAVIS_BUILD_DIR:/app --privileged --name clair-singularity --link clair --entrypoint '/bin/sh' clair-singularity -c pytest tests/ --cov clair_singularity --cov-report term-missing

fi
