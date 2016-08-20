#!/bin/bash
set -e

cp -f /etc/ssl/certs/postgresql.crt "$PGDATA/server.crt"
cp -f /etc/ssl/private/postgresql.key "$PGDATA/server.key"
chown postgres "$PGDATA/server.crt"
chown postgres "$PGDATA/server.key"
chmod og-rwx "$PGDATA/server.key"

sed -i "s|#\?ssl \?=.*|ssl = on|g" "$PGDATA/postgresql.conf"
sed -i "s|host all all 0|hostssl all all 0|g" "$PGDATA/pg_hba.conf"
