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
    curl \
    libffi \
    postgresql-client \
    postgresql-libs \
    redis

# Install build and binary dependencies, build and cleanup
COPY ./wheelhouse/* /app/wheelhouse/
COPY ./requirements/build.txt ./requirements/binary.txt /app/requirements/
RUN apk add --no-cache --virtual .deps \
    build-base \
    libffi-dev \
    postgresql-dev && \
    pip install --no-deps --no-cache-dir --require-hashes \
        -r requirements/build.txt && \
# To build a new binary wheel and update the wheelhouse, add here:
# pip wheel --no-deps cffi==1.8.3 && \
    pip install --no-deps --no-cache-dir --require-hashes \
        -f /app/wheelhouse -r requirements/binary.txt && \
    apk del --purge .deps

# Install pure Python libraries
COPY ./requirements/python.txt /app/requirements/
RUN pip install --no-deps --no-cache-dir --require-hashes \
    -r requirements/python.txt

ENV PYTHONPATH $PYTHONPATH:/app
EXPOSE 8000

COPY . /app

# Call setup.py to create scripts
RUN chown app:app /app
RUN python setup.py develop
RUN python -c "import compileall; compileall.compile_dir('miracle', quiet=1)"

# Symlink version object to serve /__version__ endpoint
RUN rm /app/miracle/static/version.json ; \
    ln -s /app/version.json /app/miracle/static/version.json

USER app
