#!/bin/sh

exec gunicorn -b :${PORT:-8000} -c python:miracle.web.settings miracle.web.app:application
