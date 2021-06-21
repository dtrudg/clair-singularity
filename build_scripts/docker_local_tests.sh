#!/bin/sh

set -e
set -u
set -x

docker stop clair-db clair || true
docker rm clair-db clair || true

docker pull arminc/clair-db:2021-06-14
docker run -d --name clair-db arminc/clair-db:2021-06-14

sleep 5

docker pull arminc/clair-local-scan:v2.1.7_5125fde67edee46cb058a3feee7164af9645e07d
docker run -p 6060:6060 --link clair-db:postgres -d --name clair arminc/clair-local-scan:v2.1.7_5125fde67edee46cb058a3feee7164af9645e07d

docker rm clair-singularity || true
docker build -t clair-singularity .
docker run --privileged --name clair-singularity --link clair --entrypoint '/bin/sh' clair-singularity -c pytest tests/ --cov clair_singularity --cov-report term-missing

docker stop clair-db clair clair-singularity || true
docker rm clair-db clair clair-singularity || true

