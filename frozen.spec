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
added_files += copy_metadata('ansys-aedt-toolkits-radar_explorer')
added_files += copy_metadata('ansys-tools-visualization_interface')
added_files += collect_data_files('rfc3987_syntax', includes=['**/*'])

if is_linux:
    added_files +=[(os.path.join(ASSETS_PATH, 'scripts'), 'assets')]

# Collect all matplotlib data, binaries, and hidden imports
mpl_datas, mpl_binaries, mpl_hidden = collect_all('matplotlib')

# Collect PyVista and its dependencies
pv_datas, pv_binaries, pv_hidden = collect_all('pyvista')
vtk_datas, vtk_binaries, vtk_hidden = collect_all('vtk')
imageio_datas, imageio_binaries, imageio_hidden = collect_all('imageio')
meshio_datas, meshio_binaries, meshio_hidden = collect_all('meshio')

# Collect other required packages
ansys_datas, ansys_binaries, ansys_hidden = collect_all('ansys')

# Combine all datas, binaries, and hidden imports
all_datas = mpl_datas + pv_datas + vtk_datas + imageio_datas + meshio_datas + ansys_datas
all_binaries = mpl_binaries + pv_binaries + vtk_binaries + imageio_binaries + meshio_binaries + ansys_binaries
all_hidden = (mpl_hidden + pv_hidden + vtk_hidden + imageio_hidden +
              meshio_hidden + ansys_hidden)

# Add manual hidden imports for PyVista and visualization
all_hidden += [
    'ansys.tools.visualization_interface',
    'pyvista.plotting',
    'pyvista.core',
    'scipy',
    'numpy',
]

a = Analysis([main_py],
             pathex=[],
             binaries=all_binaries,
             datas=added_files + all_datas,
             hiddenimports=all_hidden + ['vtkmodules', 'vtkmodules.all'],
             hookspath=['installer/hooks'],
             runtime_hooks=['installer/hooks/rthook_mpl.py'],
             excludes=['matplotlib.tests', 'vtk.test', 'vtkmodules.test'],
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
          console=True,
          icon=ICON_FILE)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name=OUT_PATH)
