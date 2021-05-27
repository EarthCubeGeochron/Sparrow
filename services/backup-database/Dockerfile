FROM rclone/rclone

RUN apk --update add --no-cache postgresql-client

COPY ./ /conf/

ENTRYPOINT /conf/backup-command
