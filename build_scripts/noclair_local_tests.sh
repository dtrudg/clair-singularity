#!/bin/bash

set -e
set -u

pytest tests/ -v -m "not needs_clair" --cov clair_singularity --cov-report term-missing
