#!/usr/bin/env bash
# Add "0 * * * * /ABSOLUTE_PATH_TO_SCRIPT/gatherfromsources.cron.sh" to your crontab

SCRIPT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SCRIPT_DIRECTORY/../../../../"
source env/bin/activate
cd fngs
python3 manage.py gatherfromsources ALL 1
