import glob
import os
import sys

from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata, collect_data_files, collect_dynamic_libs
from ansys.aedt.core import is_linux

block_cipher = None

# path where this file is located
try:
    THIS_PATH = os.path.dirname(__file__)
except NameError:
    THIS_PATH = os.getcwd()

OUT_PATH = 'radar_explorer_toolkit'
APP_NAME = 'radar_explorer_toolkit' if is_linux else 'Radar Explorer Toolkit'

CODE_PATH = os.path.join(THIS_PATH, 'src/ansys/aedt/toolkits/radar_explorer')
INSTALLER_PATH = os.path.join(THIS_PATH, 'installer')
ASSETS_PATH = os.path.join(INSTALLER_PATH, 'assets')
ICON_FILE = os.path.join(ASSETS_PATH, 'splash_icon.ico')

# consider testing paths
main_py = os.path.join(CODE_PATH, 'run_toolkit.py')

if not os.path.isfile(main_py):
    raise FileNotFoundError(f'Unable to locate main entrypoint at {main_py}')

added_files = [
    (os.path.join(ASSETS_PATH, 'radar_explorer.png'), 'assets'),
    (os.path.join(ASSETS_PATH, 'splash_icon.ico'), 'assets'),
    (os.path.join(INSTALLER_PATH, 'VERSION'), '.'),
]

# Missing metadata
added_files += copy_metadata('ansys-tools-visualization_interface')
added_files += copy_metadata('ansys-aedt-toolkits-radar_explorer')

if is_linux:
    added_files +=[(os.path.join(ASSETS_PATH, 'scripts'), 'assets')]

added_files += collect_data_files('rfc3987_syntax', includes=['**/*'])

hidden = [
    'ansys.aedt.toolkits.radar_explorer.backend.run_backend',
    'ansys.aedt.toolkits.radar_explorer.ui.run_frontend',
]

# --- Matplotlib ---
mpl_datas, mpl_binaries, mpl_hidden = collect_all('matplotlib')
mpl_hidden += collect_submodules('matplotlib.backends')
mpl_hidden += ['matplotlib.backends.backend_qtagg', 'matplotlib.backends.backend_agg']

# --- PySide6 plugins ---
pyside6_datas = collect_data_files('PySide6', includes=['Qt/plugins/**', 'Qt/translations/**'])

# --- PyAEDT / AEDT core ---
pyaedt_bins = collect_dynamic_libs('pyaedt') \
           + collect_dynamic_libs('ansys.aedt.core')

pyaedt_hidden = collect_submodules('pyaedt') \
             + collect_submodules('ansys.aedt.core')

a = Analysis([main_py],
             pathex=[],
             binaries=[] + mpl_binaries + pyaedt_bins,
             datas=added_files + mpl_datas + pyside6_datas,
             hiddenimports=hidden + mpl_hidden + pyaedt_hidden,
             hookspath=['installer/hooks'],
             runtime_hooks=['installer/hooks/rthook_mpl.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=APP_NAME,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          icon=ICON_FILE)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name=OUT_PATH)
