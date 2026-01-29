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

"""
API Test Configuration Module.

-----------------------------

Description
===========
This module contains the configuration and fixture for the pytest-based tests for the API.

The default configuration can be changed by placing a file called local_config.json.
An example of the contents of local_config.json:

{
  "desktop_version": "2025.1",
  "non_graphical": false,
  "use_grpc": true
}

You can enable the API log file in the backend_properties.json.

"""

from pathlib import Path

import pytest

from ansys.aedt.core import Desktop
from ansys.aedt.toolkits.radar_explorer.backend.api import ToolkitBackend
from tests.backend.conftest import DEFAULT_CONFIG
from tests.backend.conftest import read_local_config
from tests.backend.conftest import setup_aedt_settings

# Setup config
config = DEFAULT_CONFIG.copy()
local_cfg = read_local_config()
config.update(local_cfg)

# Update AEDT settings
setup_aedt_settings(config)

VERSION = config["desktop_version"]
NONGRAPHICAL = config["non_graphical"]


@pytest.fixture(scope="session", autouse=True)
def desktop(common_temp_dir):
    desktop = Desktop(VERSION, NONGRAPHICAL, True)
    desktop.odesktop.SetTempDirectory(str(common_temp_dir))
    desktop.disable_autosave()
    port = desktop.port
    test_session_info = {"version": VERSION, "non_graphical": NONGRAPHICAL, "port": port}
    yield test_session_info
    desktop = Desktop(VERSION, NONGRAPHICAL, False, port=port)
    desktop.release_desktop(close_projects=True, close_on_exit=True)


@pytest.fixture()
def toolkit(logger, common_temp_dir):
    """Initialize toolkit with common API."""
    logger.info("AEDTCommon API initialization")
    toolkit = ToolkitBackend()

    car = Path(common_temp_dir) / "input_data" / "geometries" / "car_stl.stl"
    rv_glb = Path(common_temp_dir) / "input_data" / "geometries" / "rv.glb"
    rv_obj = Path(common_temp_dir) / "input_data" / "geometries" / "rv1.obj"

    toolkit.properties.cad.input_file = [car, rv_glb, rv_obj]

    # Restore project
    aedt_file_archived = Path(common_temp_dir) / "input_data" / "TriHedral_RCS.aedtz"
    aedt_file = Path(common_temp_dir) / "input_data" / "trihedral.aedt"

    new_properties = {
        "aedt_version": VERSION,
        "non_graphical": NONGRAPHICAL,
        "use_grpc": config["use_grpc"],
    }
    toolkit.set_properties(new_properties)
    toolkit.launch_aedt()
    toolkit.connect_aedt()
    toolkit.desktop.odesktop.RestoreProjectArchive(str(aedt_file_archived), str(aedt_file), False, True)
    toolkit.desktop.save_project()
    toolkit.release_aedt()
    toolkit.launch_aedt()
    toolkit.release_aedt()

    yield toolkit

    toolkit.release_aedt(True, True)
