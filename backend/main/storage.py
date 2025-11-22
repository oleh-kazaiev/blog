import os

from storages.backends.s3boto3 import S3Boto3Storage


class StaticRootS3Boto3Storage(S3Boto3Storage):
    """Storage for collected static files (collectstatic)."""

    location = 'static'
    default_acl = 'public-read'

    def __init__(self, *args, **kwargs):
        """Initialise the static storage backend and adjust endpoints."""
        super().__init__(*args, **kwargs)
        # Use S3_DOMAIN for public URL generation (via Traefik/Cloudflare)
        s3_domain = os.environ['S3_DOMAIN']
        bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']

        # Set custom domain to include bucket for path-style URLs
        self.custom_domain = f'{s3_domain}/{bucket_name}'
        # Use HTTPS by default (Cloudflare handles SSL)
        if 'localhost' in s3_domain:
            self.secure_urls = False
            self.url_protocol = 'http:'


class MediaRootS3Boto3Storage(S3Boto3Storage):
    """Storage for user uploaded media files (no overwrite)."""

    location = 'media'
    file_overwrite = False
    default_acl = 'public-read'

    def __init__(self, *args, **kwargs):
        """Initialise the media storage backend and adjust endpoints."""
        super().__init__(*args, **kwargs)
        # Use S3_DOMAIN for public URL generation (via Traefik/Cloudflare)
        s3_domain = os.environ['S3_DOMAIN']
        bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']

        # Set custom domain to include bucket for path-style URLs
        self.custom_domain = f'{s3_domain}/{bucket_name}'
        # Use HTTPS by default (Cloudflare handles SSL)
        if 'localhost' in s3_domain:
            self.secure_urls = False
            self.url_protocol = 'http:'
