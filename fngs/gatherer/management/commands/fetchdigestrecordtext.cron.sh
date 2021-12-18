#!/usr/bin/env bash
# Add "* * * * * /ABSOLUTE_PATH_TO_SCRIPT/fetchdigestrecordtext.cron.sh" to your crontab

SCRIPT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SCRIPT_DIRECTORY/../../../../"
source env/bin/activate
cd fngs
python3 manage.py fetchdigestrecordtext -r -s
