#!/usr/bin/env bash

REPOSITORY=/home/ubuntu/team5-server

cd $REPOSITORY
git pull

source venv/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.deploy
python manage.py makemigrations
python manage.py migrate

sudo systemctl gunicorn restart
sudo systemctl nginx restart
