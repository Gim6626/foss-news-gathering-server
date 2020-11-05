#!/usr/bin/env bash

SCRIPT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SCRIPT_DIRECTORY/../../../../"
source env/bin/activate
cd fngs
python3 manage.py gatherfromsources ALL 1
