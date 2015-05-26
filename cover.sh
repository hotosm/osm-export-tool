#!/bin/bash

# coverage integration with nose is broken: 
# https://github.com/django-nose/django-nose/issues/2

coverage run  --branch --source=jobs,api,tasks ./manage.py test 
#coverage report
coverage html -d cover

