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
from unittest.mock import patch

from PySide6.QtCore import Qt

from ansys.aedt.toolkits.radar_explorer.ui.run_frontend import ApplicationWindow


@patch("ansys.aedt.toolkits.radar_explorer.ui.run_frontend.ApplicationWindow.check_connection", return_value=False)
def test_backend_not_connected(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    assert not windows.settings_menu.signal_flag


@patch(
    "ansys.aedt.toolkits.radar_explorer.ui.run_frontend.ApplicationWindow.get_properties",
    return_value={"aedt_version": "25.1"},
)
def test_backend_connected(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    assert windows.settings_menu.signal_flag


@patch("ansys.aedt.toolkits.radar_explorer.ui.run_frontend.ApplicationWindow.installed_versions", return_value=[])
def test_no_aedt_installed(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    assert windows.settings_menu.signal_flag


def test_home_menu_clicked(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    assert not windows.home_menu.load_rcs_button.isEnabled()

    fake_menu = MagicMock()
    fake_menu.objectName.return_value = "home_menu_custom"
    windows.ui.get_selected_menu = MagicMock(return_value=fake_menu)
    windows.home_menu.file_mode = False
    windows.home_menu.is_loaded = False

    windows.ui.left_menu.select_only_one = MagicMock()
    qtbot.mouseClick(windows.ui.left_menu.menu, Qt.LeftButton)
    assert windows.home_menu.load_rcs_button.isEnabled()


@patch("ansys.aedt.toolkits.radar_explorer.ui.run_frontend.ApplicationWindow.check_connection", return_value=False)
def test_settings_menu_clicked(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()

    fake_menu = MagicMock()
    fake_menu.objectName.return_value = "top_settings"
    windows.ui.get_selected_menu = MagicMock(return_value=fake_menu)

    windows.ui.is_right_column_visible = MagicMock(return_value=False)
    windows.ui.is_left_column_visible = MagicMock(return_value=True)
    qtbot.mouseClick(windows.ui.title_bar.menu, Qt.LeftButton)
    windows.ui.get_selected_menu.assert_called()
    windows.ui.is_right_column_visible.assert_called()
    windows.ui.is_left_column_visible.assert_called()


def test_progress_menu_clicked(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()

    fake_menu = MagicMock()
    fake_menu.objectName.return_value = "progress_menu"
    windows.ui.get_selected_menu = MagicMock(return_value=fake_menu)

    windows.ui.is_progress_visible = MagicMock(return_value=True)
    qtbot.mouseClick(windows.ui.left_menu.menu, Qt.LeftButton)
    windows.ui.get_selected_menu.assert_called()
    windows.ui.is_progress_visible.assert_called()


def test_close_menu_clicked_hides_left_column_when_not_settings(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()

    selected_menu = MagicMock()
    selected_menu.objectName.return_value = "some_menu"
    windows.ui.get_selected_menu = MagicMock(return_value=selected_menu)

    windows.ui.is_left_column_visible = MagicMock(return_value=True)
    windows.ui.toggle_left_column = MagicMock()
    windows.ui.left_menu.deselect_all = MagicMock()

    windows.close_menu_clicked()

    selected_menu.set_active.assert_called_once_with(False)
    windows.ui.toggle_left_column.assert_called_once()
    windows.ui.left_menu.deselect_all.assert_called_once()


def test_close_menu_clicked_hides_right_column_when_settings(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()

    selected_menu = MagicMock()
    selected_menu.objectName.return_value = "top_settings"
    windows.ui.get_selected_menu = MagicMock(return_value=selected_menu)

    windows.ui.is_right_column_visible = MagicMock(return_value=True)
    windows.ui.toggle_right_column = MagicMock()

    windows.close_menu_clicked()

    windows.ui.toggle_right_column.assert_called_once()


def test_incident_wave_clicked_opens_panel_and_reparents_plotter(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    windows.home_menu.is_independent = False

    selected_menu = MagicMock()
    selected_menu.objectName.return_value = "incident_menu"
    windows.ui.get_selected_menu = MagicMock(return_value=selected_menu)

    # Stub UI API
    windows.ui.left_menu.select_only_one = MagicMock()
    windows.ui.set_page = MagicMock()
    windows.ui.set_left_column_menu = MagicMock()
    windows.ui.is_left_column_visible = MagicMock(return_value=False)
    windows.ui.toggle_left_column = MagicMock()
    windows.ui.images_load.icon_path = MagicMock(return_value="icon_incident_wave.svg")

    # Stub menu object
    windows.incident_wave_menu = MagicMock()
    windows.incident_wave_menu.incident_wave_menu_widget = object()
    windows.incident_wave_menu.incident_wave_column_widget = object()
    windows.incident_wave_menu.class_name = "IncidentWaveMenu"
    windows.incident_wave_menu.plotter = MagicMock()

    windows.incident_wave_clicked()

    windows.ui.left_menu.select_only_one.assert_called_once_with("incident_menu")
    selected_menu.set_active.assert_called_once_with(True)
    windows.ui.set_page.assert_called_once_with(windows.incident_wave_menu.incident_wave_menu_widget)
    windows.ui.set_left_column_menu.assert_called_once()
    windows.ui.toggle_left_column.assert_called_once()  # because visibility returned False
    windows.incident_wave_menu.plotter.reparent_to_placeholder.assert_called_once_with("IncidentWaveMenu")


def test_mode_select_clicked_sets_page_and_left_menu(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    windows.home_menu.is_independent = False

    selected_menu = MagicMock()
    selected_menu.objectName.return_value = "mode_menu"
    windows.ui.get_selected_menu = MagicMock(return_value=selected_menu)

    windows.ui.left_menu.select_only_one = MagicMock()
    windows.ui.set_page = MagicMock()
    windows.ui.set_left_column_menu = MagicMock()
    windows.ui.is_left_column_visible = MagicMock(return_value=False)
    windows.ui.toggle_left_column = MagicMock()
    windows.ui.images_load.icon_path = MagicMock(return_value="icon_mode.svg")

    windows.mode_select_menu = MagicMock()
    windows.mode_select_menu.mode_menu_widget = object()
    windows.mode_select_menu.mode_select_column_widget = object()
    windows.mode_select_menu.class_name = "ModeSelectMenu"
    windows.mode_select_menu.plotter = MagicMock()

    windows.mode_select_clicked()

    windows.ui.left_menu.select_only_one.assert_called_once_with("mode_menu")
    selected_menu.set_active.assert_called_once_with(True)
    windows.ui.set_page.assert_called_once_with(windows.mode_select_menu.mode_menu_widget)
    windows.ui.set_left_column_menu.assert_called_once()
    windows.ui.toggle_left_column.assert_called_once()
    windows.mode_select_menu.plotter.reparent_to_placeholder.assert_called_once_with("ModeSelectMenu")


def test_solver_setup_clicked_sets_left_menu_and_toggles_left(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()
    windows.home_menu.is_independent = False

    selected_menu = MagicMock()
    selected_menu.objectName.return_value = "solve_menu"
    windows.ui.get_selected_menu = MagicMock(return_value=selected_menu)

    windows.ui.left_menu.select_only_one = MagicMock()
    windows.ui.set_left_column_menu = MagicMock()
    windows.ui.is_left_column_visible = MagicMock(return_value=False)
    windows.ui.toggle_left_column = MagicMock()
    windows.ui.images_load.icon_path = MagicMock(return_value="icon_solve.svg")

    windows.solver_setup_menu = MagicMock()
    windows.solver_setup_menu.solver_setup_column_widget = object()

    windows.solver_setup_clicked()

    windows.ui.left_menu.select_only_one.assert_called_once_with("solve_menu")
    selected_menu.set_active.assert_called_once_with(True)
    windows.ui.set_left_column_menu.assert_called_once()
    windows.ui.toggle_left_column.assert_called_once()


def test_post_2d_clicked_sets_page_updates_column_and_opens_left(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()

    selected_menu = MagicMock()
    selected_menu.objectName.return_value = "post_2d_menu"
    windows.ui.get_selected_menu = MagicMock(return_value=selected_menu)

    windows.ui.left_menu.select_only_one = MagicMock()
    windows.ui.set_page = MagicMock()
    windows.ui.set_left_column_menu = MagicMock()
    windows.ui.is_left_column_visible = MagicMock(return_value=False)
    windows.ui.toggle_left_column = MagicMock()
    windows.ui.images_load.icon_path = MagicMock(return_value="icon_plot_2d.svg")

    windows.post_2d_menu = MagicMock()
    windows.post_2d_menu.post_2d_menu_widget = object()
    windows.post_2d_menu.post_2d_column_widget = object()
    windows.post_2d_menu.update_column = MagicMock()

    windows.post_2d_clicked()

    windows.ui.left_menu.select_only_one.assert_called_once_with("post_2d_menu")
    selected_menu.set_active.assert_called_once_with(True)
    windows.ui.set_page.assert_called_once_with(windows.post_2d_menu.post_2d_menu_widget)
    windows.ui.set_left_column_menu.assert_called_once()
    windows.post_2d_menu.update_column.assert_called_once()
    windows.ui.toggle_left_column.assert_called_once()


def test_post_3d_clicked_sets_page_updates_column_and_reparents(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()

    selected_menu = MagicMock()
    selected_menu.objectName.return_value = "post_3d_menu"
    windows.ui.get_selected_menu = MagicMock(return_value=selected_menu)

    windows.ui.left_menu.select_only_one = MagicMock()
    windows.ui.set_page = MagicMock()
    windows.ui.set_left_column_menu = MagicMock()
    windows.ui.is_left_column_visible = MagicMock(return_value=False)
    windows.ui.toggle_left_column = MagicMock()
    windows.ui.images_load.icon_path = MagicMock(return_value="icon_plot_3d.svg")

    windows.post_3d_menu = MagicMock()
    windows.post_3d_menu.post_3d_menu_widget = object()
    windows.post_3d_menu.post_3d_column_widget = object()
    windows.post_3d_menu.update_column = MagicMock()
    windows.post_3d_menu.class_name = "Post3DMenu"
    windows.post_3d_menu.plotter = MagicMock()

    windows.post_3d_clicked()

    windows.ui.left_menu.select_only_one.assert_called_once_with("post_3d_menu")
    selected_menu.set_active.assert_called_once_with(True)
    windows.ui.set_page.assert_called_once_with(windows.post_3d_menu.post_3d_menu_widget)
    windows.ui.set_left_column_menu.assert_called_once()
    windows.post_3d_menu.update_column.assert_called_once()
    windows.ui.toggle_left_column.assert_called_once()
    windows.post_3d_menu.plotter.reparent_to_placeholder.assert_called_once_with("Post3DMenu")


def test_help_menu_clicked_sets_page_and_left_menu(patched_window_methods, qtbot, patch_plotter):
    windows = ApplicationWindow()

    selected_menu = MagicMock()
    selected_menu.objectName.return_value = "help_menu"
    windows.ui.get_selected_menu = MagicMock(return_value=selected_menu)

    windows.ui.left_menu.select_only_one = MagicMock()
    windows.ui.set_page = MagicMock()
    windows.ui.set_left_column_menu = MagicMock()
    windows.ui.is_left_column_visible = MagicMock(return_value=False)
    windows.ui.toggle_left_column = MagicMock()
    windows.ui.images_load.icon_path = MagicMock(return_value="help.svg")

    windows.help_menu = MagicMock()
    windows.help_menu.plot_design_menu_widget = object()
    windows.help_menu.plot_design_column_widget = object()

    windows.help_menu_clicked()

    windows.ui.left_menu.select_only_one.assert_called_once_with("help_menu")
    selected_menu.set_active.assert_called_once_with(True)
    windows.ui.set_page.assert_called_once_with(windows.help_menu.plot_design_menu_widget)
    windows.ui.set_left_column_menu.assert_called_once()
    windows.ui.toggle_left_column.assert_called_once()
