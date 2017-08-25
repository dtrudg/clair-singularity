#!/bin/sh
docker pull arminc/clair-db:2017-08-21
docker run -d --name db arminc/clair-db:2017-08-21

docker pull arminc/clair-local-scan:v2.0.0
docker run -p 6060:6060 --link db:postgres -d --name clair arminc/clair-local-scan:v2.0.0

docker rm clair_singularity
docker build -t clair_singularity .
docker run --privileged --name clair-singularity --link clair:clair clair_singularity pytest tests/ --cov clair_singularity --cov-report term-missing
