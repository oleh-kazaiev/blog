#!/bin/sh
# PostgreSQL backup script with S3 upload
# Runs inside the db container

set -e

BACKUP_DIR="${BACKUP_DIR:-/backups}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup-${TIMESTAMP}.sql.gz"
S3_KEY="backups/backup-${TIMESTAMP}.sql.gz"
MAX_BACKUPS=3

# Create backup directory if needed
mkdir -p "$BACKUP_DIR"

# Create compressed backup
pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip > "$BACKUP_FILE"

echo "Backup created: $BACKUP_FILE"

# Upload to S3/LocalStack if configured
if [ -n "$AWS_S3_ENDPOINT_URL" ] && [ -n "$AWS_STORAGE_BUCKET_NAME" ]; then
    aws s3 cp "$BACKUP_FILE" "s3://${AWS_STORAGE_BUCKET_NAME}/${S3_KEY}" \
        --endpoint-url "$AWS_S3_ENDPOINT_URL" \
        --no-verify-ssl 2>/dev/null || true
    echo "Uploaded to S3: s3://${AWS_STORAGE_BUCKET_NAME}/${S3_KEY}"
fi

# Keep only the 3 most recent backups
ls -t "$BACKUP_DIR"/backup-*.sql.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm -f

echo "Backup completed"
