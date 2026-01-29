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

import os
from pathlib import Path
import sys
from typing import Dict
from typing import List

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

from pydantic import BaseModel
from pydantic import Field

from ansys.aedt.toolkits.common.ui.models import UIProperties
from ansys.aedt.toolkits.common.ui.models import general_settings
import ansys.aedt.toolkits.radar_explorer

DEFAULT_ANGLE_VALUE = "0.0deg"


class RadarExplorerProperties(BaseModel):
    """Stores Radar Explorer Toolkit properties."""

    # Precision
    precision: int = 4

    # Plotter
    all_scene_actors: Dict = Field(default_factory=dict)
    reports: Dict = Field(default_factory=dict)
    solution_names: List = Field(default_factory=list)
    metadata_files: List = Field(default_factory=list)
    configuration_file: str = ""
    model_units: str = "meter"

    # RCS Plotter
    num_contours: int = 10

    # Incident wave
    rotation: str = "ZYZ"
    angle1: str = DEFAULT_ANGLE_VALUE
    angle2: str = DEFAULT_ANGLE_VALUE
    angle3: str = DEFAULT_ANGLE_VALUE

    # Mode Menu
    select_mode: str = "Range Profile"
    center_frequency: str = "10.0GHz"

    # Range
    range_mode: str = "System"
    fft_bandwidth: str = "1.0GHz"
    frequencies: str = "101"
    maximum_range: str = "15.1395m"
    range_resolution: str = "0.1499m"

    # Azimuth
    azimuth_mode: str = "System"
    azimuth_span: str = "6.0deg"
    azimuth_angles: str = "101"
    maximum_cross_range_azimuth: str = "14.314m"
    cross_range_azimuth_resolution: str = "0.1417m"

    # Elevation
    elevation_mode: str = "System"
    elevation_span: str = "4.0deg"
    elevation_angles: str = "101"
    maximum_cross_range_elevation: str = "21.4711m"
    cross_range_elevation_resolution: str = "0.2126m"

    # Solver
    ray_density: str = "4.0"
    bounces: str = "3"
    fast_frequency_looping: bool = False
    ptd_utd: bool = False
    cores: str = "4"
    solve_interactive: bool = False


class FrontendProperties(BaseModel):
    """Stores Radar Explorer Toolkit properties."""

    radar_explorer: RadarExplorerProperties


class Properties(FrontendProperties, UIProperties, validate_assignment=True):
    """Stores all properties."""


frontend_properties = {}

installation_folder = Path(ansys.aedt.toolkits.radar_explorer.__file__).parent

if "PYAEDT_TOOLKIT_CONFIG_DIR" in os.environ:
    local_dir = Path(os.environ["PYAEDT_TOOLKIT_CONFIG_DIR"]).resolve()
    frontend_config = local_dir / "frontend_properties.toml"
    if frontend_config.is_file():  # pragma: no cover
        with frontend_config.open("rb") as file_handler:
            frontend_properties = tomllib.load(file_handler)

if not frontend_properties and (installation_folder / "ui/frontend_properties.toml").is_file():
    with (installation_folder / "ui/frontend_properties.toml").open("rb") as file_handler:
        frontend_properties = tomllib.load(file_handler)

toolkit_property = {}
if frontend_properties:
    for frontend_key in frontend_properties:
        if frontend_key == "defaults":
            for toolkit_key in frontend_properties["defaults"]:
                if hasattr(general_settings, toolkit_key):
                    setattr(general_settings, toolkit_key, frontend_properties["defaults"][toolkit_key])
        else:
            toolkit_property[frontend_key] = frontend_properties[frontend_key]

new_common_properties = {}
for common_key in general_settings:
    new_common_properties[common_key[0]] = common_key[1]

properties = Properties(**toolkit_property, **new_common_properties)
