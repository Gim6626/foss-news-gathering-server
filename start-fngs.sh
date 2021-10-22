#!/usr/bin/env bash
if [ -z $1 ]
then
  echo "Usage: $0 PORT"
  exit 1
fi
set -e
set -u
PORT=$1
SCRIPT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SCRIPT_DIRECTORY"
source env/bin/activate
cd fngs
gunicorn --bind=0.0.0.0:$PORT -w $(( 2 * `cat /proc/cpuinfo | grep 'core id' | wc -l` + 1 )) fngs.wsgi
