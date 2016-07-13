# miracle
#
# VERSION 0.1

FROM python:3.5-alpine
MAINTAINER https://mail.mozilla.org/listinfo/testpilot-dev

# add a non-privileged user for installing and running
# the application
RUN addgroup -g 10001 app && \
    adduser -D -u 10001 -G app -h /app -s /sbin/nologin app

WORKDIR /app

# Run the web service by default.
ENTRYPOINT ["/app/conf/run.sh"]
CMD ["web"]

# install dependencies, cleanup
COPY ./requirements.txt /app/requirements.txt
RUN apk add --update build-base zlib-dev linux-headers && \
    pip install --upgrade --no-cache-dir pip && \
    pip install --no-deps --no-cache-dir -r requirements.txt && \
    apk del --purge build-base gcc

ENV PYTHONPATH $PYTHONPATH:/app
EXPOSE 8000

COPY . /app

# symlink version object to serve /__version__ endpoint
RUN rm /app/miracle/static/version.json ; \
    ln -s /app/version.json /app/miracle/static/version.json

USER app
