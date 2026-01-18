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

from pathlib import Path
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

from typing import Dict
from typing import List
from typing import Union

from pydantic import BaseModel
from pydantic import Field

from ansys.aedt.toolkits.common.backend.models import CommonProperties
from ansys.aedt.toolkits.common.backend.models import common_properties
import ansys.aedt.toolkits.radar_explorer


class RadarProperties(BaseModel):
    """Store properties for the Radar Explorer Toolkit."""

    model: Dict[str, List[str]] = Field(default_factory=dict)
    units: str = "meter"
    rotation_order: str = "ZYZ"
    rotation_ang1: float = 0.0
    rotation_ang2: float = 0.0
    rotation_ang3: float = 0.0
    calculation_type: str = "Range Profile"
    aspect_ang_phi: float = 6.0
    aspect_ang_theta: float = 4.0
    num_phi: int = 201
    num_theta: int = 201
    range_max: float = 1.0
    range_max_az: float = 1.0
    range_max_el: float = 1.0
    range_res: float = 0.5
    range_res_az: float = 0.5
    range_res_el: float = 0.5


class RadarSetup(BaseModel):
    """Store properties for the Radar Explorer Toolkit."""

    ray_density: float = 1.0
    num_bounces: int = 3
    ffl: bool = True
    ptd_utd: bool = True
    solve_interactive: bool = True
    center_freq: float = 10.0e9
    fft_bandwidth: float = 1.0e9
    sim_freq_lower: float = 1.0e9
    sim_freq_upper: float = 1.0e9
    num_freq: int = 101
    plane_wave_names: str = ""
    setup_name: str = "rcs_setup"
    sweep_name: str = "Sweep"
    num_cores: int = 4


class RadarCAD(BaseModel):
    """Store CAD information for the Radar Explorer Toolkit."""

    input_file: List[str] = Field(default_factory=list)
    material: List[str] = Field(default_factory=list)
    position: List[List[Union[float, int, str]]] = Field(default_factory=list)
    model_units: str = "meter"


class BackendProperties(BaseModel):
    """Store toolkit properties."""

    radar: RadarProperties
    setup: RadarSetup
    cad: RadarCAD


class Properties(BackendProperties, CommonProperties, validate_assignment=True):
    """Store all properties."""


installation_folder = Path(ansys.aedt.toolkits.radar_explorer.__file__).parent

backend_properties = {}
if (installation_folder / "backend/backend_properties.toml").is_file():
    with (installation_folder / "backend/backend_properties.toml").open("rb") as file_handler:
        backend_properties = tomllib.load(file_handler)

toolkit_property = {}
if backend_properties:
    for backend_key in backend_properties:
        if backend_key == "defaults":
            for toolkit_key in backend_properties["defaults"]:
                if hasattr(common_properties, toolkit_key):
                    setattr(common_properties, toolkit_key, backend_properties["defaults"][toolkit_key])
        else:
            toolkit_property[backend_key] = backend_properties[backend_key]

new_common_properties = {}
for common_key in common_properties:
    new_common_properties[common_key[0]] = common_key[1]

properties = Properties(**toolkit_property, **new_common_properties)
