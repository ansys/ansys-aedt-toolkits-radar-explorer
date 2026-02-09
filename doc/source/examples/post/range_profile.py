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
.. _ref_range_profile:

Generate a range profile plot from RCS metadata
=============================================

This example demonstrates how to generate a range profile plot from RCS metadata.
It loads RCS data from multiple polarizations and visualizes the range profile.
"""


# ## Perform required imports

from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSData
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter

# ## Get metadata

metadata_vh = r"..\example_models\range_profile_data\VH_Spheres_Range.json"
metadata_hh = r"..\example_models\range_profile_data\HH_Spheres_Range.json"
metadata_vv = r"..\example_models\range_profile_data\VV_Spheres_Range.json"
metadata_hv = r"..\example_models\range_profile_data\HV_Spheres_Range.json"

# ## Load RCS

rcs_data_vh = MonostaticRCSData(metadata_vh)
rcs_data_hh = MonostaticRCSData(metadata_hh)
rcs_data_vv = MonostaticRCSData(metadata_vv)
rcs_data_hv = MonostaticRCSData(metadata_hv)

# Get range profile

data_vh = rcs_data_vh.range_profile
data_hh = rcs_data_hh.range_profile
data_vv = rcs_data_vv.range_profile
data_hv = rcs_data_hv.range_profile

# ## Load RCS plotter

rcs_data_vh_plotter = MonostaticRCSPlotter(rcs_data_vh)

# ## Plot 2D range profile

rcs_data_vh_plotter.plot_range_profile()

# ## Plot scene with geometry

rcs_data_vh_plotter.show_geometry = True
rcs_data_vh_plotter.plot_scene()

# ## Plot range profile settings using the internal Plotter

rcs_data_vh_plotter.add_range_profile_settings(size_range=20, range_resolution=1)
rcs_data_vh_plotter.plot_scene()

# ## Plot range profile

rcs_data_vh_plotter.show_geometry = True
rcs_data_vh_plotter.add_range_profile(color_bar="red")
rcs_data_vh_plotter.plot_scene()

# ## Plot range profile results disabling one plot

for range_profile_actors in rcs_data_vh_plotter.all_scene_actors["annotations"]["range_profile"].values():
    range_profile_actors.custom_object.show = False
rcs_data_vh_plotter.plot_scene()

# ## Clear scene and plot range profile using internal plotter

rcs_data_vh_plotter.clear_scene()
rcs_data_vh_plotter.show_geometry = False
rcs_data_vh_plotter.add_range_profile()
rcs_data_vh_plotter.plot_scene()

# ## Plot some range profile results

range_profile_name = list(rcs_data_vh_plotter.all_scene_actors["results"]["range_profile"].keys())[0]
rcs_data_vh_plotter.clear_scene(first_level="results", second_level="range_profile", name=range_profile_name)
rcs_data_vh_plotter.add_range_profile(plot_type="ribbon")
rcs_data_vh_plotter.add_range_profile(plot_type="Plane H")
rcs_data_vh_plotter.add_range_profile(plot_type="Plane V")
rcs_data_vh_plotter.plot_scene()

# ## Plot some range profile projection

rcs_data_vh_plotter.clear_scene()
rcs_data_vh_plotter.add_range_profile(plot_type="Projection")
rcs_data_vh_plotter.plot_scene()

# ## Plot some range profile rotated

rcs_data_vh_plotter.clear_scene()
rcs_data_vh_plotter.show_geometry = True
rcs_data_vh_plotter.add_range_profile(plot_type="Rotated")
rcs_data_vh_plotter.plot_scene()

# ## Plot some range profile extruded

rcs_data_vh_plotter.clear_scene()
rcs_data_vh_plotter.show_geometry = True
rcs_data_vh_plotter.add_range_profile(plot_type="Extruded")
rcs_data_vh_plotter.plot_scene()

# ## Move plot in Z

# Clean results.

rcs_data_vh_plotter.clear_scene()
rcs_data_vh_plotter.show_geometry = True

# Add range profiles.

rcs_data_vh_plotter.add_range_profile(color_bar="red")
rcs_data_vh_plotter.add_range_profile(color_bar="red")

# Get second plot and change properties.

range_profile_result = rcs_data_vh_plotter.all_scene_actors["results"]["range_profile"]["range_profile_1"]
range_profile_result.custom_object.color = None
range_profile_result.custom_object.color_map = "jet"

# Move plot.

range_profile_result.custom_object.z_offset = 5.0

# Plot scene.

rcs_data_vh_plotter.plot_scene()

# ## Scale curve

# Clean results.

rcs_data_vh_plotter.clear_scene()
rcs_data_vh_plotter.show_geometry = True

# Add range profiles.

rcs_data_vh_plotter.add_range_profile()

# Get second plot and change properties

range_profile_result = rcs_data_vh_plotter.all_scene_actors["results"]["range_profile"]["range_profile_0"]
range_profile_result.custom_object.color = None
range_profile_result.custom_object.color_map = "jet"

# Move plot.

range_profile_result.custom_object.z_offset = 5.0

# Scale plot.

range_profile_result.custom_object.scale_factor = 3.0

# Plot scene.

rcs_data_vh_plotter.plot_scene()

# Move plot.

range_profile_result.custom_object.z_offset = 1.0

# Plot scene

rcs_data_vh_plotter.plot_scene()

# Reset plot.

range_profile_result.custom_object.reset_scene()

# Plot scene.

rcs_data_vh_plotter.plot_scene()
