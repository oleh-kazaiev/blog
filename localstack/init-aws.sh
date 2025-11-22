#!/bin/bash
# LocalStack initialization script
# Auto-creates S3 bucket on startup

set -e

echo "LocalStack init: Creating S3 bucket..."

# Use awslocal (LocalStack's AWS CLI wrapper)
awslocal s3 mb s3://${AWS_STORAGE_BUCKET_NAME:-blog-local-media} 2>/dev/null || true

echo "LocalStack init: S3 bucket '${AWS_STORAGE_BUCKET_NAME:-blog-local-media}' is ready"
