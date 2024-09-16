#!/bin/bash
set -xe
set -o allexport

source .env
python3 main.py

set +o allexport