#!/bin/bash

# Start the server using sudo while preserving the virtual environment
pkexec bash -c "cd /usr/local/lib/PycharmProjects/mctest && \
    source /usr/local/lib/PycharmProjects/AmbientePython3/bin/activate && \
    python3 manage.py runserver" &

# Wait for the server process to be detected
while ! netstat -tulnp 2>/dev/null | grep -q ":8000"; do
    sleep 1
done

# Open the browser in a new tab
xdg-open http://127.0.0.1:8000/ &

# Keep the shell open
exec bash