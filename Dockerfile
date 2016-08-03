# mozilla/miracle
#
# VERSION 0.1

FROM python:3.5-alpine
MAINTAINER context-graph@lists.mozilla.org

# add a non-privileged user for installing and running
# the application
RUN addgroup -g 10001 app && \
    adduser -D -u 10001 -G app -h /app -s /sbin/nologin app

WORKDIR /app

# Run the web service by default.
ENTRYPOINT ["/app/conf/run.sh"]
CMD ["web"]

# Install runtime dependencies
RUN apk add --no-cache \
    postgresql-client \
    postgresql-libs \
    redis

COPY ./wheelhouse/* /app/wheelhouse/
COPY ./requirements/* /app/requirements/

# Install build dependencies, build and cleanup
RUN apk add --no-cache --virtual .deps \
    build-base \
    postgresql-dev && \
    pip install --no-deps --no-cache-dir --require-hashes \
        -r requirements/build.txt && \
    pip install --no-deps --no-cache-dir --require-hashes \
        -f /app/wheelhouse -r requirements/binary.txt && \
    apk del --purge .deps

# Install pure Python libraries
RUN pip install --no-deps --no-cache-dir --require-hashes \
    -r requirements/python.txt

ENV PYTHONPATH $PYTHONPATH:/app
EXPOSE 8000

COPY . /app

# Call setup.py to create scripts
RUN python setup.py develop

# Symlink version object to serve /__version__ endpoint
RUN rm /app/miracle/static/version.json ; \
    ln -s /app/version.json /app/miracle/static/version.json

USER app
