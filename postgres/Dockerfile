FROM postgres:17.6-alpine

# Install dcron and AWS CLI
RUN apk add --no-cache dcron aws-cli

# Copy backup script
COPY backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh

# Setup crontab - daily backup at 2 AM
RUN echo "0 2 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1" | crontab -

# Custom entrypoint that starts cron and postgres
COPY db-entrypoint.sh /usr/local/bin/db-entrypoint.sh
RUN chmod +x /usr/local/bin/db-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/db-entrypoint.sh"]
CMD ["postgres"]
