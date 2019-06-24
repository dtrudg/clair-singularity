#!/bin/bash

set -e
set -u

echo "Running setup.py install"
python setup.py install

echo "Running tests that don't need Clair"
pytest tests/ -v -m "not needs_clair" --cov clair_singularity --cov-report term-missing

if [[ $TRAVIS_PYTHON_VERSION == "3.6"* ]]; then
    echo "Python 3.6 - running docker tests with Clair"
    docker pull arminc/clair-db:2019-06-24
    docker run -d --name clair-db arminc/clair-db:2019-06-24
    sleep 5
    docker pull arminc/clair-local-scan:v2.0.8_0ed98e9ead65a51ba53f7cc53fa5e80c92169207
    docker run -p 6060:6060 --link clair-db:postgres -d --name clair arminc/clair-local-scan:v2.0.8_0ed98e9ead65a51ba53f7cc53fa5e80c92169207
    docker ps
    docker build -t clair-singularity .

    # Clear out any old .pyc from the local tests
    find . -name *.pyc -delete

    docker run -v $TRAVIS_BUILD_DIR:/app --privileged --name clair-singularity --link clair --entrypoint '/bin/sh' clair-singularity -c pytest tests/ --cov clair_singularity --cov-report term-missing

fi
