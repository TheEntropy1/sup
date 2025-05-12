#!/bin/bash

# Run database migrations and start the application
python -c "from app import app, db; db.create_all()"
exec gunicorn -b 0.0.0.0:${PORT:-5000} main:app