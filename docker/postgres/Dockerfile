# Merge in https://github.com/docker-library/postgres/pull/152
FROM postgres:9.5

COPY enable_ssl.sh /docker-entrypoint-initdb.d/
COPY postgres_dev_ssl.pem /etc/ssl/certs/postgresql.crt
COPY postgres_dev_ssl.key /etc/ssl/private/postgresql.key
