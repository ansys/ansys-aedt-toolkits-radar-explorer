# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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

# # Generate an ISAR 2D plot from RCS metadata
#
# This example demonstrates how to use the ``ToolkitBackend`` class.
# It initiates AEDT through PyAEDT, opens an HFSS design, and proceeds to get the antenna data.


# ## Perform required imports

from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSData
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter

# ## Get metadata

metadata_vv = r"..\example_models\isar_2d_data\HH_Spheres_ISAR2D.json"

# ## Load RCS

rcs_data_vv = MonostaticRCSData(metadata_vv)

# ## Get ISAR 2D data

rcs_data_vv.upsample_azimuth = 201
data = rcs_data_vv.isar_2d

# ## Load RCS plotter

rcs_data_vv_plotter = MonostaticRCSPlotter(rcs_data_vv)

# ## Plot 2D ISAR data

rcs_data_vv_plotter.plot_isar_2d()

# ## Plot 2D ISAR settings

rcs_data_vv_plotter.add_isar_2d_settings(size_range=18, size_cross_range=12)
rcs_data_vv_plotter.plot_scene()

# ## Plot ISAR

rcs_data_vv_plotter.clear_scene()
rcs_data_vv_plotter.add_isar_2d()
rcs_data_vv_plotter.plot_scene()

# ## Plot ISAR 2D with relief

rcs_data_vv_plotter.clear_scene()
rcs_data_vv_plotter.add_isar_2d(plot_type="Relief")
rcs_data_vv_plotter.plot_scene()

# ## Plot ISAR 2D with projection

# rcs_data_vv_plotter.clear_scene()
# rcs_data_vv_plotter.add_isar_2d()
# rcs_data_vv_plotter.add_isar_2d(plot_type="Projection")
# rcs_data_vv_plotter.plot_scene()
