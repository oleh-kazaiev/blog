#!/bin/sh
set -e

# Start cron daemon in background
crond -b -l 8

# Execute original postgres entrypoint
exec docker-entrypoint.sh "$@"
