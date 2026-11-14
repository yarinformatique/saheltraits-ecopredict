#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python -c "print('Running database migrations if needed...')"
alembic upgrade head || true
