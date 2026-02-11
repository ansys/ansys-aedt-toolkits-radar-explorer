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

from PySide6.QtCore import Qt

from ansys.aedt.toolkits.common.ui.utils.widgets.py_logger.py_logger import PyLogger
from ansys.aedt.toolkits.radar_explorer.ui.run_frontend import ApplicationWindow
from ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu import HomeMenu
from ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu import properties
from ansys.aedt.toolkits.radar_explorer.ui.windows.post_2d.post_2d_menu import Post2DMenu
from ansys.aedt.toolkits.radar_explorer.ui.windows.post_3d.post_3d_menu import Post3DMenu

DUMMY_JSON_FILE = "dummy.json"


class MockMonostaticRCSData:
    def __init__(self, frequencies, available_incident_wave_theta, available_incident_wave_phi):
        self.frequencies = frequencies
        self.available_incident_wave_theta = available_incident_wave_theta
        self.available_incident_wave_phi = available_incident_wave_phi

    @property
    def rcs_data(self):
        return self


dummy_rcs_objects_rcs = {"dummy_name": {"dummy_data": MockMonostaticRCSData([1e9], [0, 45, 90], [45])}}


@patch.object(PyLogger, "log")
def test_load_rcs_file_mode_metadata_mock_rcs(mock_log, patched_window_methods, qtbot, patch_plotter):
    """Test loading RCS information in file mode with metadata file enabling 2D and 3D post (category RCS)."""
    window = ApplicationWindow()
    menu = window.home_menu

    with (
        patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(DUMMY_JSON_FILE, None)),
        patch(
            "ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu.read_json",
            return_value={"model_info": "dummy_model"},
        ),
        patch.object(HomeMenu, "load_rcs_metadatada"),
        patch.object(properties.radar_explorer, "all_scene_actors", {"plotter": dummy_rcs_objects_rcs}),
    ):
        qtbot.mouseClick(menu.browse, Qt.LeftButton)
        qtbot.mouseClick(menu.load_rcs_button, Qt.LeftButton)

        assert any("Loading RCS information" in call.args[0] for call in mock_log.call_args_list)
        assert window.post_2d_menu.category_combobox.currentText() == "RCS"
        assert window.post_3d_menu.category_combobox.currentText() == "RCS"
        assert any("RCS data loaded successfully" in call.args[0] for call in mock_log.call_args_list)
        assert menu.is_loaded


dummy_rcs_objects_3d_isar = {"dummy_name": {"dummy_data": MockMonostaticRCSData([1e9, 2e9], [0, 45, 90], [0, 45])}}


@patch.object(PyLogger, "log")
def test_load_rcs_file_mode_metadata_mock_rcs_3d_isar(mock_log, patched_window_methods, qtbot, patch_plotter):
    """Test loading RCS information in file mode with metadata file enabling 2D and 3D post (category 3D ISAR)."""
    window = ApplicationWindow()
    menu = window.home_menu

    with (
        patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(DUMMY_JSON_FILE, None)),
        patch(
            "ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu.read_json",
            return_value={"model_info": "dummy_model"},
        ),
        patch.object(HomeMenu, "load_rcs_metadatada"),
        patch.object(properties.radar_explorer, "all_scene_actors", {"plotter": dummy_rcs_objects_3d_isar}),
        patch.object(Post2DMenu, "update_solution"),
        patch.object(Post3DMenu, "update_solution"),
    ):
        qtbot.mouseClick(menu.browse, Qt.LeftButton)
        qtbot.mouseClick(menu.load_rcs_button, Qt.LeftButton)

        assert any("Loading RCS information" in call.args[0] for call in mock_log.call_args_list)
        assert window.post_2d_menu.category_combobox.currentText() == "3D ISAR"
        assert window.post_3d_menu.category_combobox.currentText() == "3D ISAR"
        assert any("RCS data loaded successfully" in call.args[0] for call in mock_log.call_args_list)
        assert menu.is_loaded


dummy_rcs_objects_2d_isar = {"dummy_name": {"dummy_data": MockMonostaticRCSData([1e9, 2e9], [0, 45, 90], [0])}}


@patch.object(PyLogger, "log")
def test_load_rcs_file_mode_metadata_mock_rcs_2d_isar(mock_log, patched_window_methods, qtbot, patch_plotter):
    """Test loading RCS information in file mode with metadata file enabling 2D and 3D post (category 2D ISAR)."""
    window = ApplicationWindow()
    menu = window.home_menu

    with (
        patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(DUMMY_JSON_FILE, None)),
        patch(
            "ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu.read_json",
            return_value={"model_info": "dummy_model"},
        ),
        patch.object(HomeMenu, "load_rcs_metadatada"),
        patch.object(properties.radar_explorer, "all_scene_actors", {"plotter": dummy_rcs_objects_2d_isar}),
        patch.object(Post2DMenu, "update_solution"),
        patch.object(Post3DMenu, "update_solution"),
    ):
        qtbot.mouseClick(menu.browse, Qt.LeftButton)
        qtbot.mouseClick(menu.load_rcs_button, Qt.LeftButton)

        assert any("Loading RCS information" in call.args[0] for call in mock_log.call_args_list)
        assert window.post_2d_menu.category_combobox.currentText() == "2D ISAR"
        assert window.post_3d_menu.category_combobox.currentText() == "2D ISAR"
        assert any("RCS data loaded successfully" in call.args[0] for call in mock_log.call_args_list)
        assert menu.is_loaded


dummy_rcs_objects_range_profile = {"dummy_name": {"dummy_data": MockMonostaticRCSData([1e9, 2e9], [0], [0])}}


@patch.object(PyLogger, "log")
def test_load_rcs_file_mode_metadata_mock_rcs_range_profile(mock_log, patched_window_methods, qtbot, patch_plotter):
    """Test loading RCS information in file mode with metadata file enabling 2D and 3D post (category range profile)."""
    window = ApplicationWindow()
    menu = window.home_menu

    with (
        patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(DUMMY_JSON_FILE, None)),
        patch(
            "ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu.read_json",
            return_value={"model_info": "dummy_model"},
        ),
        patch.object(HomeMenu, "load_rcs_metadatada"),
        patch.object(properties.radar_explorer, "all_scene_actors", {"plotter": dummy_rcs_objects_range_profile}),
        patch.object(Post2DMenu, "update_solution"),
        patch.object(Post3DMenu, "update_solution"),
    ):
        qtbot.mouseClick(menu.browse, Qt.LeftButton)
        qtbot.mouseClick(menu.load_rcs_button, Qt.LeftButton)

        assert any("Loading RCS information" in call.args[0] for call in mock_log.call_args_list)
        assert window.post_2d_menu.category_combobox.currentText() == "Range Profile"
        assert window.post_3d_menu.category_combobox.currentText() == "Range Profile"
        assert any("RCS data loaded successfully" in call.args[0] for call in mock_log.call_args_list)
        assert menu.is_loaded
