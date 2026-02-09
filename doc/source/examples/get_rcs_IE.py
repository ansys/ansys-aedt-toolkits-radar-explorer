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
.. _ref_get_rcs_ie:

Create RCS setup from existing HFSS design
========================================

This example demonstrates how to use the ``ToolkitBackend`` class.
It initiates AEDT through PyAEDT, opens a HFSS design, creates a 3D Component and imports it in a new SBR+ design.
Finally it creates the setup and proceeds to analyze.
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

# ##  Set AEDT version
#
# Set AEDT version.

aedt_version = "2025.1"

# ## Set non-graphical mode
#
# Set non-graphical mode.

non_graphical = False

# ## Set number of cores

cores = 4

# ## Create temporary directory

temp_dir = tempfile.TemporaryDirectory(suffix="_ansys")

# ## Example project

original = r"example_models\ogive-IE.aedtz"
project_name = Path(temp_dir.name) / "ogive-IE.aedtz"
shutil.copy(original, project_name)

# ## Initialize toolkit
#
# Initialize the toolkit.

toolkit_api = ToolkitBackend()

# ## Set properties
#
# Set non-graphical mode.

new_properties = {"non_graphical": non_graphical, "aedt_version": aedt_version}
flag1, msg1 = toolkit_api.set_properties(new_properties)

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

# ## Open project
#
# Open the project.

open_msg = toolkit_api.open_project(project_name)

# ## Set setup properties

toolkit_api.properties.setup.setup_name = "Setup1"
toolkit_api.properties.setup.sweep_name = "LastAdaptive"

# ## Get RCS data
#
# Direct export

rcs_metadata = toolkit_api.export_rcs(excitation="IncPWave1", encode=False)

# ## Save and release AEDT

toolkit_api.release_aedt(True, True)

# ## Load RCS data

rcs_data = MonostaticRCSData(rcs_metadata)

# ## Load RCS Plotter

rcs_data_plotter = MonostaticRCSPlotter(rcs_data)

# ## Select cut

primary_sweep = "IWavePhi"
secondary_sweep_value = rcs_data_plotter.rcs_data.incident_wave_theta

# ## Plot RCS

plot = rcs_data_plotter.plot_rcs(primary_sweep=primary_sweep, secondary_sweep_value=secondary_sweep_value)

plot_freq = rcs_data_plotter.plot_rcs(primary_sweep="Freq", secondary_sweep="IWavePhi")

# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean temporary directory

temp_dir.cleanup()
