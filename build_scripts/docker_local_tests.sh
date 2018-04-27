#!/bin/sh

set -e
set -u

docker stop clair-db clair || true
docker rm clair-db clair || true

docker pull arminc/clair-db:2018-04-01
docker run -d --name clair-db arminc/clair-db:2018-04-01

sleep 5

docker pull arminc/clair-local-scan:v2.0.1
docker run -p 6060:6060 --link clair-db:postgres -d --name clair arminc/clair-local-scan:v2.0.1

docker rm clair-singularity || true
docker build -t clair-singularity .
docker run --privileged --name clair-singularity --link clair clair-singularity pytest tests/ --cov clair_singularity --cov-report term-missing

docker stop clair-db clair clair-singularity || true
docker rm clair-db clair clair-singularity || true

