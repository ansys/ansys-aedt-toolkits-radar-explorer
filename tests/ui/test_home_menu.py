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

from unittest.mock import patch

from PySide6.QtCore import Qt

from ansys.aedt.toolkits.common.ui.utils.widgets.py_logger.py_logger import PyLogger
from ansys.aedt.toolkits.radar_explorer.ui.run_frontend import ApplicationWindow
from ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu import AVAILABLE_UNITS
from ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu import PROJECTION_CATEGORIES_LIST
from ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu import HomeMenu
from ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu import properties

DUMMY_JSON_FILE = "dummy.json"
DUMMY_STL_FILE = "dummy.stl"


def test_3d_settings_menu_default_values(patched_window_methods, qtbot, patch_plotter):
    """Test the default values of the projection and model unit menus in the application window."""
    window = ApplicationWindow()
    menu = window.home_menu

    qtbot.mouseClick(menu.model_setting_icon, Qt.LeftButton)

    box = menu.projection_menu
    assert PROJECTION_CATEGORIES_LIST == [box.itemText(i) for i in range(box.count())]
    assert PROJECTION_CATEGORIES_LIST[0] == box.currentText()

    box = menu.model_unit_menu
    assert AVAILABLE_UNITS == [box.itemText(i) for i in range(box.count())]
    assert AVAILABLE_UNITS[0] == box.currentText()


def test_change_projection_and_units(patched_window_methods, qtbot, patch_plotter):
    """Test changing the projection and model unit values in the application window."""
    window = ApplicationWindow()
    menu = window.home_menu

    qtbot.mouseClick(menu.model_setting_icon, Qt.LeftButton)

    box = menu.projection_menu
    box.setCurrentIndex(1)
    assert PROJECTION_CATEGORIES_LIST[1] == box.currentText()
    assert properties.radar_explorer.all_scene_actors["plotter"]["parallel"]
    box.setCurrentIndex(0)
    assert PROJECTION_CATEGORIES_LIST[0] == box.currentText()
    assert not properties.radar_explorer.all_scene_actors["plotter"]["parallel"]

    box = menu.model_unit_menu
    box.setCurrentIndex(3)
    assert AVAILABLE_UNITS[3] == box.currentText()
    assert properties.radar_explorer.model_units == AVAILABLE_UNITS[3]


@patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(DUMMY_JSON_FILE, None))
def test_browse_file_mode(mock_get_open, patched_window_methods, qtbot, patch_plotter):
    """Test the browse button of the home menu in file mode."""
    window = ApplicationWindow()
    menu = window.home_menu
    qtbot.mouseClick(menu.browse, Qt.LeftButton)

    mock_get_open.assert_called_once()
    assert DUMMY_JSON_FILE == menu.file.text()


@patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(DUMMY_STL_FILE, None))
def test_browse_aedt_mode(mock_get_open, patched_window_methods, qtbot, patch_plotter):
    """Test the browse button of the home menu in AEDT / Import geometry mode."""
    window = ApplicationWindow()
    menu = window.home_menu
    qtbot.mouseClick(menu.toggle, Qt.LeftButton)
    qtbot.mouseClick(menu.aedt_toggle, Qt.LeftButton)
    qtbot.mouseClick(menu.browse, Qt.LeftButton)

    mock_get_open.assert_called_once()
    assert DUMMY_STL_FILE == menu.file.text()


@patch.object(PyLogger, "log")
def test_toggle_file_to_aedt_mode(mock_log, patched_window_methods, qtbot, patch_plotter):
    """Test toggling between AEDT and File mode in the home menu."""
    window = ApplicationWindow()
    menu = window.home_menu
    assert not menu.toggle.isChecked()
    assert menu.file_mode

    qtbot.mouseClick(menu.toggle, Qt.LeftButton)
    assert menu.toggle.isChecked()
    assert not menu.file_mode
    assert any("AEDT mode menu" in call.args[0] for call in mock_log.call_args_list)

    qtbot.mouseClick(menu.toggle, Qt.LeftButton)
    assert not menu.toggle.isChecked()
    assert menu.file_mode
    assert any("File mode menu" in call.args[0] for call in mock_log.call_args_list)


@patch.object(PyLogger, "log")
def test_toggle_aedt_states(mock_log, patched_window_methods, qtbot, patch_plotter):
    """Test toggling between import geometry and load design menu in AEDT mode of the home menu."""
    window = ApplicationWindow()
    menu = window.home_menu
    qtbot.mouseClick(menu.toggle, Qt.LeftButton)
    assert not menu.aedt_toggle.isChecked()

    qtbot.mouseClick(menu.aedt_toggle, Qt.LeftButton)
    assert menu.aedt_toggle.isChecked()
    assert any("Import geometry menu" in call.args[0] for call in mock_log.call_args_list)

    qtbot.mouseClick(menu.aedt_toggle, Qt.LeftButton)
    assert not menu.aedt_toggle.isChecked()
    assert any("Load design menu" in call.args[0] for call in mock_log.call_args_list)


@patch.object(PyLogger, "log")
def test_toggle_solved_states(mock_log, patched_window_methods, qtbot, patch_plotter):
    """Test toggling between solved states in AEDT mode of the home menu."""
    window = ApplicationWindow()
    menu = window.home_menu
    qtbot.mouseClick(menu.toggle, Qt.LeftButton)
    assert not menu.solved_toggle.isChecked()

    qtbot.mouseClick(menu.solved_toggle, Qt.LeftButton)
    assert menu.solved_toggle.isChecked()
    assert any("New solution" in call.args[0] for call in mock_log.call_args_list)

    qtbot.mouseClick(menu.solved_toggle, Qt.LeftButton)
    assert not menu.solved_toggle.isChecked()
    assert any("Get solution" in call.args[0] for call in mock_log.call_args_list)


@patch.object(PyLogger, "log")
def test_load_rcs_file_mode_metadata_empty_rcs_objects(mock_log, patched_window_methods, qtbot, patch_plotter):
    """Test loading RCS information in file mode with metadata file and empty rcs_objects."""
    window = ApplicationWindow()
    menu = window.home_menu

    with (
        patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(DUMMY_JSON_FILE, None)),
        patch(
            "ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu.read_json",
            return_value={"model_info": "dummy_model"},
        ),
        patch.object(HomeMenu, "load_rcs_metadatada"),
        patch.object(properties.radar_explorer, "all_scene_actors", {"plotter": {}}),
    ):
        qtbot.mouseClick(menu.browse, Qt.LeftButton)
        qtbot.mouseClick(menu.load_rcs_button, Qt.LeftButton)

        assert any("Loading RCS information" in call.args[0] for call in mock_log.call_args_list)
        assert any("Configuration loaded successfully" in call.args[0] for call in mock_log.call_args_list)
        assert menu.is_loaded


@patch.object(PyLogger, "log")
def test_load_rcs_file_mode_config_file_empty_rcs_objects(mock_log, patched_window_methods, qtbot, patch_plotter):
    """Test loading RCS information in file mode with config file and empty rcs_objects."""
    window = ApplicationWindow()
    menu = window.home_menu

    with (
        patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(DUMMY_JSON_FILE, None)),
        patch(
            "ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu.read_json",
            return_value={"metadata_files": "dummy_metadata", "model_info": "dummy_model"},
        ),
        patch.object(HomeMenu, "load_rcs_metadatada"),
        patch.object(properties.radar_explorer, "all_scene_actors", {"plotter": {}}),
    ):
        qtbot.mouseClick(menu.browse, Qt.LeftButton)
        qtbot.mouseClick(menu.load_rcs_button, Qt.LeftButton)

        assert any("Loading RCS information" in call.args[0] for call in mock_log.call_args_list)
        assert any("Configuration loaded successfully" in call.args[0] for call in mock_log.call_args_list)
        assert menu.is_loaded


@patch(
    "ansys.aedt.toolkits.radar_explorer.ui.run_frontend.ApplicationWindow.get_properties",
    return_value={"active_design": "dummy_design"},
)
@patch.object(PyLogger, "log")
def test_load_rcs_aedt_mode_import_geometry(mock_log, patched_window_methods, qtbot, patch_plotter):
    """Test loading RCS information in AEDT mode importing geometry."""
    window = ApplicationWindow()
    menu = window.home_menu
    qtbot.mouseClick(menu.toggle, Qt.LeftButton)
    qtbot.mouseClick(menu.aedt_toggle, Qt.LeftButton)

    with (
        patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(DUMMY_STL_FILE, None)),
        patch.object(window, "insert_cad_design") as mock_insert,
        patch.object(window, "export_rcs") as mock_export,
        patch.object(HomeMenu, "load_rcs_metadatada"),
    ):
        qtbot.mouseClick(menu.browse, Qt.LeftButton)
        qtbot.mouseClick(menu.load_rcs_button, Qt.LeftButton)

        import_cad_thread = menu.import_cad_thread
        assert import_cad_thread.isRunning()
        qtbot.waitUntil(lambda: not import_cad_thread.isRunning(), timeout=20000)

        mock_insert.assert_called_once()
        mock_export.assert_called_once()
        assert any("Importing CAD and inserting new design" in call.args[0] for call in mock_log.call_args_list)
        assert any("CAD imported successfully" in call.args[0] for call in mock_log.call_args_list)
        assert menu.is_loaded
