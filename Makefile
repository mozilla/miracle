.PHONY: all postgres

all:
	@echo "No default target."

DB_HOST ?= `docker inspect --format '{{ .NetworkSettings.IPAddress }}' miracle_postgres`
DB_RET ?= 1
postgres:
	# Wait to confirm that Postgres has started.
	@DB_RET=$(DB_RET); \
	while [ $${DB_RET} -ne 0 ] ; do \
		echo "Trying Postgres..." ; \
	    nc -z $(DB_HOST) 5432 ; \
		DB_RET=$$? ; \
	    sleep 0.5 ; \
	    done; \
	true
