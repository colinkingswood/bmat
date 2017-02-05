#!/bin/bash

# to run this, I am assuming you are on a Linux machine, with Python3 sqllite, and virtualenv installed.
# You may  need to adjust some things such as the location of the system Python3 interpreter
# I created this using Linux Mint, so it should work on

# 1: create a directory for the web service code
mkdir bmat_test
cd bmat_test

## create a directory for the virtualenv
mkdir python3-env
cd python3-env

# create a virtualenv using python3
virtualenv . --no-site-packages -p /usr/bin/python3

# activate our virtualenv
. bin/activate

# move back to the parent directory and clone the code from git
cd ..
git clone https://github.com/colinkingswood/bmat.git

# move to teh top level folder of the web service code
cd bmat

# install the python dependencies
echo `pip install -r requirements.txt`

# run django migrations to create the database tables
python manage.py migrate

# run the django development server.
python manage.py runserver

# The web service should be running in 127.0.0.1:8000
