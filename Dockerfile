# mozilla/miracle
#
# VERSION 1.0

FROM python:3.5-slim
MAINTAINER context-graph@lists.mozilla.org

# add a non-privileged user for installing and running
# the application
RUN groupadd -g 10001 app && \
    useradd -M -u 10001 -g 10001 -G app -d /app -s /sbin/nologin app

WORKDIR /app

# Run the web service by default.
ENTRYPOINT ["/app/conf/run.sh"]
EXPOSE 8000
CMD ["web"]

# Disable installing doc/man/locale files
RUN echo "\
path-exclude=/usr/share/doc/*\n\
path-exclude=/usr/share/man/*\n\
path-exclude=/usr/share/locale/*\n\
" > /etc/dpkg/dpkg.cfg.d/apt-no-docs

# Install normal dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        curl \
        file \
        gcc \
        libffi-dev \
        make \
        redis-tools \
        sudo \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Add Postgres repository and install Postgres 9.5
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main 9.5" \
    >> /etc/apt/sources.list && \
    curl -s https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
        libpq5=9.5\* \
        libpq-dev=9.5\* \
        libssl-dev \
        postgresql-client-9.5 \
    && rm -rf /var/lib/apt/lists/*

# Install Rust into app users home directory
RUN mkdir -p /app && \
    mkdir -p /app/miracle_rlib && \
    chown -R app:app /app
USER app
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH=/app/.cargo/bin:$PATH
USER root

# Install build and binary Python libraries
COPY ./requirements/build.txt ./requirements/binary.txt /app/requirements/
RUN pip install --no-deps --no-cache-dir --require-hashes \
        -r requirements/build.txt && \
    pip install --no-deps --no-cache-dir --require-hashes \
        -r requirements/binary.txt

# Install pure Python libraries
COPY ./requirements/python.txt /app/requirements/
RUN pip install --no-deps --no-cache-dir --require-hashes \
    -r requirements/python.txt

# Install Rust dependencies and build Rust library
USER app
COPY ./miracle_rlib /app/miracle_rlib
RUN cd /app/miracle_rlib; make release; cd /app
USER root

# Install application code
COPY . /app
ENV PYTHONPATH $PYTHONPATH:/app
RUN chown -R app:app /app && \
    python setup.py develop && \
    python -c "import compileall; compileall.compile_dir('miracle', quiet=1)"

# Symlink version object to serve /__version__ endpoint
RUN rm /app/miracle/static/version.json ; \
    ln -s /app/version.json /app/miracle/static/version.json

# Drop down to unprivileged user
USER app
