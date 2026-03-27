#!/bin/sh
set -e

python -m app.wait_for_db

if ls migrations/versions/*.py >/dev/null 2>&1; then
  flask --app app:create_app db upgrade
else
  python -m app.create_db
fi

exec "$@"
