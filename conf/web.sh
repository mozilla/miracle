#!/bin/sh

exec gunicorn -b :${PORT:-8080} -c python:miracle.web.settings miracle.web.app:application
