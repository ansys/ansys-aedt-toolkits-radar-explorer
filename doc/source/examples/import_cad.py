# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. _ref_import_cad:

Import CAD and create ISAR 2D setup
===================================

This example demonstrates how to use the ``ToolkitBackend`` class.
It initiates AEDT through PyAEDT, opens an SBR+ design, creates the setup, and analyzes it.
"""


# ## Perform required imports

from pathlib import Path
import shutil
import sys
import tempfile
import time

from ansys.aedt.toolkits.radar_explorer.backend.api import ToolkitBackend
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSData
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter

# ## Set AEDT version

aedt_version = "2025.1"

# ## Set non-graphical mode

non_graphical = True

# ## Set number of cores

cores = 4

# ## Create temporary directory

temp_dir = tempfile.TemporaryDirectory(suffix="_ansys")

# ## Get example project

car_original = r"example_models\geometries\car_stl.stl"
car_original_path = Path(Path(__file__).parent, car_original)
car = Path(temp_dir.name) / "car.stl"
shutil.copy(car_original_path, car)

# ## Initialize toolkit

toolkit_api = ToolkitBackend()

# ## Get toolkit properties

properties_from_backend = toolkit_api.get_properties()

# ## Set properties
#
# Set non-graphical mode.

set_properties = {"non_graphical": non_graphical, "aedt_version": aedt_version}
flag_set_properties, msg_set_properties = toolkit_api.set_properties(set_properties)

# ## Initialize AEDT
#
# Launch a new AEDT session in a thread.

thread_msg = toolkit_api.launch_thread(toolkit_api.launch_aedt)

# ## Wait for the toolkit thread to be idle
#
# Wait for the toolkit thread to be idle and ready to accept a new task.

idle = toolkit_api.wait_to_be_idle()
if not idle:
    print("AEDT not initialized.")
    sys.exit()

# ## Connect design
#
# Connect an existing design or create a new design.

toolkit_api.connect_design("HFSS")

# ## Import CAD

toolkit_api.properties.cad.input_file = [car]
toolkit_api.properties.cad.material = ["pec"]
toolkit_api.properties.cad.position = [[0.0, 0.0, 0.0]]

# ## Set calculation type

new_properties = {"calculation_type": "2D ISAR"}

flag3, msg3 = toolkit_api.set_properties(new_properties)

new_properties = {"ray_density": 0.1, "ffl": True, "num_cores": cores}
flag4, msg4 = toolkit_api.set_properties(new_properties)

# ## Set ISAR 2D properties

new_properties = {
    "range_max_az": 14.3,
    "range_res_az": 0.15,
    "range_max": 15.0,
    "range_res": 0.15,
    "sim_freq_lower": 9.5e9,
    "sim_freq_upper": 10.5e9,
}
flag5, msg5 = toolkit_api.set_properties(new_properties)

properties1 = toolkit_api.get_properties()

toolkit_api.update_isar_2d_properties(range_is_system=False, azimuth_is_system=False)

# Check how ``aspect_ang_phi`` and ``num_phi`` has changed.

properties2 = toolkit_api.get_properties()

# ## Connect design and load project information

toolkit_api.launch_aedt()

# ## Insert CAD

toolkit_api.insert_cad_sbr()

# ## Assign excitation

v_plane_wave = toolkit_api.add_plane_wave(name="IncWaveVpol", polarization="Vertical")

# ## Create setup

setup_name = toolkit_api.add_setup()

# ## Get toolkit properties

properties = toolkit_api.get_properties()

# ## Analyze

toolkit_api.analyze()
toolkit_api.save_project()

# ## Get RCS data

rcs_metadata_vv = toolkit_api.export_rcs(v_plane_wave, "ComplexMonostaticRCSTheta", encode=False)

# ## Save and release AEDT

toolkit_api.release_aedt(True, True)

# ## Load RCS data

rcs_data_vv = MonostaticRCSData(rcs_metadata_vv)

# ## Load RCS plotter

rcs_data_vv_plotter = MonostaticRCSPlotter(rcs_data_vv)

# ## Set ISAR 2D

rcs_data_vv_plotter.plot_isar_2d()

# ## Plot ISAR

rcs_data_vv_plotter.clear_scene()
rcs_data_vv_plotter.add_isar_2d()
rcs_data_vv_plotter.plot_scene()

# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean temporary directory

temp_dir.cleanup()
