#!/usr/bin/env bash
set -e
set -u
DATABASE_USER='postgres'
DATABASE='test_fossnews'
SCRIPT_DIR="$( dirname -- "${BASH_SOURCE[0]}"; )"
DATABASE_LOG_FILE="${SCRIPT_DIR}/db.log"
echo "Dropping database"
sudo -u "${DATABASE_USER}" psql -c "DROP DATABASE ${DATABASE}" || {
  echo "Failed to drop database"
}
echo "Creating database"
sudo -u "${DATABASE_USER}" psql -c "CREATE DATABASE ${DATABASE}" || {
  echo "Failed to create database"
  exit 1
}
echo "Loading database dump"
sudo -u "${DATABASE_USER}" psql -d "${DATABASE}" < "${SCRIPT_DIR}/data/database-empty.sql" &> "${DATABASE_LOG_FILE}" || {
  echo "Failed to load database dump"
  exit 1
}
echo "Running tests"
python3 "${SCRIPT_DIR}/manage.py" test -k
