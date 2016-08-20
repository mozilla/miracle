#!/bin/sh
DB_ROOT_CERT=${DB_ROOT_CERT:-"rds_root_ca.pem"}
PGHOST=$DB_HOST PGUSER=$DB_USER PGPASSWORD=$DB_PASSWORD PGDATABASE=miracle \
PGSSLMODE="verify-ca" PGSSLROOTCERT="/app/data/$DB_ROOT_CERT" \
    psql $1 $2 $3 $4 $5 $6 $7 $8 $9
