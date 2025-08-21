#!/bin/bash

# Set variables
DESKTOP_FILE="/usr/share/applications/Mctest.desktop"
INSTALL_PATH="/usr/local/lib/PycharmProjects"
SCRIPT_PATH="$INSTALL_PATH/debian/start_mctest.sh"
ICON_PATH="$INSTALL_PATH/mctest/static/icon.png"

# Ensure the script is executable
chmod +x "$SCRIPT_PATH"

# Create the .desktop file for system-wide access
cat << EOF | sudo tee "$DESKTOP_FILE" > /dev/null
[Desktop Entry]
Name=Mctest
Comment=Launches the Mctest Server
Icon=$ICON_PATH
Exec=$SCRIPT_PATH
Type=Application
Terminal=true
Categories=Development;
EOF

# Ensure the .desktop file has the correct permissions
sudo chmod 644 "$DESKTOP_FILE"
sudo chmod +x "$SCRIPT_PATH"

# Refresh desktop database (for instant visibility)
if [ -x "$(command -v update-desktop-database)" ]; then
    sudo update-desktop-database
fi

echo "Shortcut created successfully: $DESKTOP_FILE"
