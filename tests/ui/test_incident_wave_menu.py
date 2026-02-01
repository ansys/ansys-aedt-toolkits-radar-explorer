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

from unittest.mock import MagicMock

from PySide6.QtCore import Qt

from ansys.aedt.toolkits.radar_explorer.ui.models import DEFAULT_ANGLE_VALUE
from ansys.aedt.toolkits.radar_explorer.ui.run_frontend import ApplicationWindow
from ansys.aedt.toolkits.radar_explorer.ui.windows.incident_wave.incident_wave_menu import DEFAULT_SOLUTION_NAME_LIST
from ansys.aedt.toolkits.radar_explorer.ui.windows.incident_wave.incident_wave_menu import ROTATION_ORDER_LIST


def test_incident_wave_menu_default_values(patched_window_methods, qtbot, patch_plotter):
    """Test the default values of the incident wave menu in the application window."""
    windows = ApplicationWindow()
    menu = windows.incident_wave_menu

    box = menu.solution_selection_combobox
    assert DEFAULT_SOLUTION_NAME_LIST == [box.itemText(i) for i in range(box.count())]
    assert DEFAULT_SOLUTION_NAME_LIST[0] == box.currentText()

    box = menu.rotation_combobox
    assert ROTATION_ORDER_LIST == [box.itemText(i) for i in range(box.count())]
    assert ROTATION_ORDER_LIST[0] == box.currentText()

    line = menu.angle1_textbox
    assert DEFAULT_ANGLE_VALUE == line.text()

    line = menu.angle2_textbox
    assert DEFAULT_ANGLE_VALUE == line.text()

    line = menu.angle3_textbox
    assert DEFAULT_ANGLE_VALUE == line.text()

    toggle = menu.preview_toggle
    assert not toggle.isChecked()


def test_incident_wave_menu_show_preview(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    menu_mode = windows.mode_select_menu
    incident_mode = windows.incident_wave_menu

    fake_menu = MagicMock()
    fake_menu.objectName.return_value = "incident_menu"
    windows.ui.get_selected_menu = MagicMock(return_value=fake_menu)

    windows.ui.is_progress_visible = MagicMock(return_value=True)

    menu_mode.mode_selection_combobox.setCurrentText("Range Profile")
    incident_mode.solution_selection_combobox.setCurrentText("No solution")
    qtbot.mouseClick(windows.ui.left_menu.menu, Qt.LeftButton)
    qtbot.mouseClick(incident_mode.preview_toggle, Qt.LeftButton)
    assert incident_mode.preview_toggle.isChecked()

    menu_mode.mode_selection_combobox.setCurrentText("2D ISAR")
    qtbot.mouseClick(windows.ui.left_menu.menu, Qt.LeftButton)
    qtbot.mouseClick(incident_mode.preview_toggle, Qt.LeftButton)
    assert not incident_mode.preview_toggle.isChecked()

    menu_mode.mode_selection_combobox.setCurrentText("2D ISAR")
    qtbot.mouseClick(incident_mode.preview_toggle, Qt.LeftButton)
    assert incident_mode.preview_toggle.isChecked()
    qtbot.mouseClick(incident_mode.preview_toggle, Qt.LeftButton)

    menu_mode.mode_selection_combobox.setCurrentText("3D ISAR")
    qtbot.mouseClick(incident_mode.preview_toggle, Qt.LeftButton)
    assert incident_mode.preview_toggle.isChecked()


def test_set_options_enabled(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    incident_mode = windows.incident_wave_menu
    incident_mode.set_options_enabled(True)
    assert incident_mode.angle1_textbox.isEnabled()


def test_save_status(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    incident_mode = windows.incident_wave_menu
    incident_mode.save_status()


def test_load_status(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    incident_mode = windows.incident_wave_menu
    incident_mode.load_status()


def test_update_angles(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    incident_mode = windows.incident_wave_menu
    angle1 = incident_mode.angle1_textbox.text()
    incident_mode.angle1_textbox.value = 1.0
    incident_mode.update_angle1()
    assert incident_mode.angle1_textbox.text() != angle1
    angle2 = incident_mode.angle2_textbox.text()
    incident_mode.angle2_textbox.value = 1.0
    incident_mode.update_angle2()
    assert incident_mode.angle2_textbox.text() != angle2
    angle3 = incident_mode.angle3_textbox.text()
    incident_mode.angle3_textbox.value = 1.0
    incident_mode.update_angle3()
    assert incident_mode.angle3_textbox.text() != angle3
