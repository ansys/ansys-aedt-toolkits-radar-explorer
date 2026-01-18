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

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def patched_window_methods():
    """Fixture to patch methods in ApplicationWindow for testing."""
    with (
        patch(
            "ansys.aedt.toolkits.radar_explorer.ui.run_frontend.ApplicationWindow.check_connection", return_value=True
        ),
        patch("ansys.aedt.toolkits.radar_explorer.ui.run_frontend.ApplicationWindow.get_properties", return_value={}),
        patch(
            "ansys.aedt.toolkits.radar_explorer.ui.run_frontend.ApplicationWindow.installed_versions",
            return_value=["25.1"],
        ),
        patch("ansys.aedt.toolkits.radar_explorer.ui.run_frontend.SettingsMenu.process_id", return_value=12345),
    ):
        yield


@pytest.fixture
def patch_plotter():
    """Fixture used to avoid VTK error when UI is closed."""
    with patch("ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu.Common3DPlotter"):
        yield
