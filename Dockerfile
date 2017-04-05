FROM python:3.6-slim

# add a non-privileged user for installing and running
# the application
RUN groupadd -g 10001 app && \
    useradd -M -u 10001 -g 10001 -G app -d /app -s /sbin/nologin app

WORKDIR /app

# Run the web service by default.
ENTRYPOINT ["/app/conf/run.sh"]
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
        redis-tools \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Install build and binary Python libraries
COPY ./requirements/build.txt ./requirements/binary.txt /app/requirements/
RUN buildDeps=' \
        gcc \
        libffi-dev \
        libssl-dev \
        make \
    ' && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends $buildDeps && \
    pip install --no-deps --no-cache-dir --require-hashes \
        -r requirements/build.txt && \
    pip install --no-deps --no-cache-dir --require-hashes \
        -r requirements/binary.txt && \
    apt-get purge -y --auto-remove $buildDeps && \
    rm -rf /var/lib/apt/lists/*

# Install pure Python libraries
COPY ./requirements/python.txt /app/requirements/
RUN pip install --no-deps --no-cache-dir --require-hashes \
    -r requirements/python.txt

ENV PYTHONPATH $PYTHONPATH:/app
EXPOSE 8080

COPY . /app

# Call setup.py to create scripts
RUN chown app:app /app
RUN python setup.py develop
RUN python -c "import compileall; compileall.compile_dir('miracle', quiet=1)"

# Symlink version object to serve /__version__ endpoint
RUN rm /app/miracle/static/version.json ; \
    ln -s /app/version.json /app/miracle/static/version.json

# Drop down to unprivileged user
USER app
