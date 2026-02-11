#!/bin/bash

# Create the .local/share/applications directory if it doesn't exist
mkdir -p ${HOME}/.local/share/applications

# Check if the radar desktop file exists
if [ ! -f "${HOME}/.local/share/applications/radar_explorer_toolkit_prebuild.desktop" ]; then
    echo "Warning: Radar desktop file not found. Desktop shortcut may not be created."
    exit 1
fi

# Process the desktop file to substitute environment variables and create the final desktop file
envsubst < ${HOME}/.local/share/applications/radar_explorer_toolkit_prebuild.desktop > ${HOME}/.local/share/applications/radar_explorer_toolkit.desktop

# Check if the processed desktop file was created successfully
if [ ! -f "${HOME}/.local/share/applications/radar_explorer_toolkit.desktop" ]; then
    echo "Error: Failed to create desktop file."
    exit 1
fi

# Remove the radar file (keeping the processed one)
rm -f ${HOME}/.local/share/applications/radar_explorer_toolkit_prebuild.desktop

# Make the desktop file executable
chmod +x ${HOME}/.local/share/applications/radar_explorer_toolkit.desktop

# Update desktop database to register the new application
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database ${HOME}/.local/share/applications
fi

echo "Desktop shortcut created successfully."
