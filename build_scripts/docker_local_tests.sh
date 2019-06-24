#!/bin/sh

set -e
set -u
set -x

docker stop clair-db clair || true
docker rm clair-db clair || true

docker pull arminc/clair-db:2019-06-24
docker run -d --name clair-db arminc/clair-db:2019-06-24

sleep 5

docker pull arminc/clair-local-scan:v2.0.8_0ed98e9ead65a51ba53f7cc53fa5e80c92169207
docker run -p 6060:6060 --link clair-db:postgres -d --name clair arminc/clair-local-scan:v2.0.8_0ed98e9ead65a51ba53f7cc53fa5e80c92169207

docker rm clair-singularity || true
docker build -t clair-singularity .
docker run --privileged --name clair-singularity --link clair --entrypoint '/bin/sh' clair-singularity -c pytest tests/ --cov clair_singularity --cov-report term-missing

docker stop clair-db clair clair-singularity || true
docker rm clair-db clair clair-singularity || true

