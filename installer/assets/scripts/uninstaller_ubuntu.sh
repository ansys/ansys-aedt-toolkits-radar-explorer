echo "Uninstalling Radar Explorer Toolkit......."
sleep 3

rm -rf ${HOME}/.local/share/applications/radar_explorer_toolkit.desktop
rm -rf ${HOME}/.local/usr/share/doc/radar_explorer_toolkit

rm -rf ${HOME}/.local/opt/radar_explorer_toolkit

sed -i '/# Add alias for Ansys Radar Explorer Toolkit/d' ~/.bashrc
sed -i  '/alias  radar_explorer_toolkit/d' ~/.bashrc