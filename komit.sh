#!/bin/bash
set -xe
set -o allexport

source .env
python3 main.py


# Disable exporting of variables to the environment
set +o allexport