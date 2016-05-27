#!/bin/sh

exec gunicorn -b :${PORT:-8000} -c python:contextgraph.web.settings contextgraph.web.app:application
