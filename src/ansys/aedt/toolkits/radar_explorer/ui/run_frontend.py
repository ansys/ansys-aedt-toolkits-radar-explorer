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
import sys

# isort: off
from ansys.aedt.toolkits.radar_explorer import __version__

# Default user interface properties
from ansys.aedt.toolkits.radar_explorer.ui.models import properties

# isort: on

# PySide6 Widgets
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow

from ansys.aedt.toolkits.common.ui.common_windows.settings_column import SettingsMenu

# Import general common frontend modules
from ansys.aedt.toolkits.common.ui.logger_handler import logger

# Common windows
from ansys.aedt.toolkits.common.ui.main_window.main_window_layout import MainWindowLayout
from ansys.aedt.toolkits.common.ui.utils.resolution import set_pyside_resolution

# Toolkit frontend API
from ansys.aedt.toolkits.radar_explorer.ui.actions import Frontend
from ansys.aedt.toolkits.radar_explorer.ui.windows.common_windows_utils import CommonWindowUtilsRCS
from ansys.aedt.toolkits.radar_explorer.ui.windows.help.help_menu import HelpMenu

# New windows
from ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_menu import HomeMenu
from ansys.aedt.toolkits.radar_explorer.ui.windows.incident_wave.incident_wave_menu import IncidentWaveMenu
from ansys.aedt.toolkits.radar_explorer.ui.windows.mode.mode_menu import ModeSelectMenu
from ansys.aedt.toolkits.radar_explorer.ui.windows.post_2d.post_2d_menu import Post2DMenu
from ansys.aedt.toolkits.radar_explorer.ui.windows.post_3d.post_3d_menu import Post3DMenu
from ansys.aedt.toolkits.radar_explorer.ui.windows.solver_setup.solver_setup_menu import SolverSetupMenu

# Windows

# Backend URL and port
if len(sys.argv) == 3:  # pragma: no cover
    properties.backend_url = sys.argv[1]
    properties.backend_port = int(sys.argv[2])

url = properties.backend_url
port = properties.backend_port

os.environ["QT_API"] = "pyside6"
os.environ["QT_FONT_DPI"] = "96"

set_pyside_resolution(properties, use_tkinter=False)

properties.version = __version__


class ApplicationWindow(QMainWindow, Frontend):
    def __init__(self):
        super().__init__()

        self.thread = None
        self.properties = properties
        self.url = f"http://{properties.backend_url}:{properties.backend_port}"
        # Scene actors
        properties.radar_explorer.all_scene_actors = {"model": {}, "annotations": {}, "results": {}, "plotter": {}}

        # General Settings

        # Create main window layout
        self.ui = MainWindowLayout(self)
        self.ui.setup()

        # Settings menu
        self.settings_menu = SettingsMenu(self)
        self.settings_menu.setup()

        self.ui.title_bar.clicked.connect(self.settings_menu_clicked)

        # Check backend connection
        success = self.check_connection()
        self.backend_connected = False

        # Populate settings column
        if not success:
            msg = "Error getting properties from backend. User interface running without backend."
            self.ui.update_logger(msg)
            logger.error(msg)
            self.settings_menu.signal_flag = False
            self.settings_menu.aedt_version.addItem("Backend OFF")
            self.settings_menu.aedt_session.addItem("Backend OFF")
        else:
            self.backend_connected = True
            # Get default properties
            be_properties = self.get_properties()
            # Get AEDT installed versions
            installed_versions = self.installed_versions()

            self.settings_menu.aedt_session.clear()
            self.settings_menu.aedt_session.addItem("New Session")

            if installed_versions:
                self.settings_menu.connect_aedt.setEnabled(True)
                for ver in installed_versions:
                    self.settings_menu.aedt_version.addItem(ver)
            else:
                self.settings_menu.aedt_version.addItem("AEDT not installed")

            if be_properties.get("aedt_version") in installed_versions:
                self.settings_menu.aedt_version.setCurrentText(be_properties.get("aedt_version"))

        # Custom toolkit setup starts here
        # Home menu
        self.home_menu = HomeMenu(self)
        self.home_menu.setup()
        self.ui.left_menu.clicked.connect(self.home_menu_clicked)

        # Incident wave menu
        self.incident_wave_menu = IncidentWaveMenu(self)
        self.incident_wave_menu.setup()
        self.ui.left_menu.clicked.connect(self.incident_wave_clicked)

        # Mode selection menu
        self.mode_select_menu = ModeSelectMenu(self)
        self.mode_select_menu.setup()
        self.ui.left_menu.clicked.connect(self.mode_select_clicked)

        # Solver setup menu
        self.solver_setup_menu = SolverSetupMenu(self)
        self.solver_setup_menu.setup()
        self.ui.left_menu.clicked.connect(self.solver_setup_clicked)

        # Plot 2D design menu
        self.post_2d_menu = Post2DMenu(self)
        self.post_2d_menu.setup()
        self.post_2d_menu.add_tab(name="Results")
        self.post_2d_menu.tab_obj.currentChanged.connect(lambda: self.post_2d_menu.add_tab())
        self.ui.left_menu.clicked.connect(self.post_2d_clicked)

        # Plot 3D design menu
        self.post_3d_menu = Post3DMenu(self)
        self.post_3d_menu.setup()
        self.ui.left_menu.clicked.connect(self.post_3d_clicked)

        CommonWindowUtilsRCS.set_visible_post_proc(self, False)

        # Help menu
        self.help_menu = HelpMenu(self)
        self.help_menu.setup()
        self.ui.left_menu.clicked.connect(self.help_menu_clicked)

        # Close column
        self.ui.title_bar.clicked.connect(self.close_menu_clicked)
        self.ui.left_menu.clicked.connect(self.progress_menu_clicked)
        self.ui.left_column.clicked.connect(self.close_menu_clicked)

        self.ui.set_page(self.ui.load_pages.home_page)

    def home_menu_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()
        self.ui.left_menu.select_only_one(selected_menu.objectName())
        if menu_name == "home_menu_custom":
            selected_menu.set_active(True)

            self.ui.set_page(self.home_menu.home_menu_widget)

            is_left_visible = self.ui.is_left_column_visible()

            self.ui.set_left_column_menu(
                menu=self.home_menu.home_column_widget,
                title=properties.add_left_menus[0]["btn_text"],
                icon_path=self.ui.images_load.icon_path(properties.add_left_menus[0]["btn_icon"]),
            )

            if not is_left_visible:
                self.ui.toggle_left_column()

            if self.backend_connected and not self.home_menu.file_mode and not self.home_menu.is_loaded:
                self.home_menu.load_rcs_button.setEnabled(True)
            self.home_menu.plotter.reparent_to_placeholder(self.home_menu.class_name)

    def settings_menu_clicked(self):
        self.ui.set_right_column_menu(title="Settings")
        selected_menu = self.ui.get_selected_menu()
        is_right_visible = self.ui.is_right_column_visible()
        if not is_right_visible:
            self.ui.toggle_right_column()

        self.home_menu.right_column_visibility(False)
        self.post_2d_menu.right_column_visibility(False)

        if not selected_menu:  # pragma: no cover
            menu_name = "top_settings"
        else:
            menu_name = selected_menu.objectName()

        is_right_visible = self.ui.is_right_column_visible()
        is_left_visible = self.ui.is_left_column_visible()

        if menu_name == "top_settings" and not is_right_visible:
            self.ui.app.settings_menu.show_widgets()
            if is_left_visible:
                self.ui.toggle_left_column()
                self.ui.left_menu.deselect_all()
            self.ui.toggle_right_column()
            self.ui.set_right_column_menu(title="Settings")

    def progress_menu_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()
        self.ui.left_menu.select_only_one(selected_menu.objectName())
        if menu_name == "progress_menu":
            is_progress_visible = self.ui.is_progress_visible()
            if is_progress_visible:
                selected_menu.set_active(False)
            self.ui.toggle_progress()

    def close_menu_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()
        if menu_name != "top_settings" and self.ui.is_left_column_visible():
            selected_menu.set_active(False)
            self.ui.toggle_left_column()
            self.ui.left_menu.deselect_all()
        if menu_name == "top_settings" and self.ui.is_right_column_visible():
            self.ui.toggle_right_column()

    def incident_wave_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()
        self.ui.left_menu.select_only_one(selected_menu.objectName())
        if menu_name == "incident_menu" and not self.home_menu.is_independent:
            selected_menu.set_active(True)

            self.ui.set_page(self.incident_wave_menu.incident_wave_menu_widget)

            self.ui.set_left_column_menu(
                menu=self.incident_wave_menu.incident_wave_column_widget,
                title="Incident Wave",
                icon_path=self.ui.images_load.icon_path("icon_incident_wave.svg"),
            )

            is_left_visible = self.ui.is_left_column_visible()
            if not is_left_visible:
                self.ui.toggle_left_column()
            self.incident_wave_menu.plotter.reparent_to_placeholder(self.incident_wave_menu.class_name)

    def mode_select_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()
        self.ui.left_menu.select_only_one(selected_menu.objectName())
        if menu_name == "mode_menu" and not self.home_menu.is_independent:
            selected_menu.set_active(True)

            self.ui.set_page(self.mode_select_menu.mode_menu_widget)

            self.ui.set_left_column_menu(
                menu=self.mode_select_menu.mode_select_column_widget,
                title="Mode Select",
                icon_path=self.ui.images_load.icon_path("icon_mode.svg"),
            )

            is_left_visible = self.ui.is_left_column_visible()
            if not is_left_visible:
                self.ui.toggle_left_column()
            self.mode_select_menu.plotter.reparent_to_placeholder(self.mode_select_menu.class_name)

    def solver_setup_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()
        self.ui.left_menu.select_only_one(selected_menu.objectName())
        if menu_name == "solve_menu" and not self.home_menu.is_independent:
            selected_menu.set_active(True)

            # self.ui.set_page(self.post_2d_menu.post_2d_menu_widget)

            self.ui.set_left_column_menu(
                menu=self.solver_setup_menu.solver_setup_column_widget,
                title="Solver Setup",
                icon_path=self.ui.images_load.icon_path("icon_solve.svg"),
            )

            is_left_visible = self.ui.is_left_column_visible()
            if not is_left_visible:
                self.ui.toggle_left_column()

    def post_2d_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()
        self.ui.left_menu.select_only_one(selected_menu.objectName())
        if menu_name == "post_2d_menu":
            selected_menu.set_active(True)
            self.ui.set_page(self.post_2d_menu.post_2d_menu_widget)

            self.ui.set_left_column_menu(
                menu=self.post_2d_menu.post_2d_column_widget,
                title="2D Postprocessing",
                icon_path=self.ui.images_load.icon_path("icon_plot_2d.svg"),
            )

            self.post_2d_menu.update_column()

            is_left_visible = self.ui.is_left_column_visible()
            if not is_left_visible:
                self.ui.toggle_left_column()

    def post_3d_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()
        self.ui.left_menu.select_only_one(selected_menu.objectName())
        if menu_name == "post_3d_menu":
            selected_menu.set_active(True)
            self.ui.set_page(self.post_3d_menu.post_3d_menu_widget)

            self.ui.set_left_column_menu(
                menu=self.post_3d_menu.post_3d_column_widget,
                title="3D Postprocessing",
                icon_path=self.ui.images_load.icon_path("icon_plot_3d.svg"),
            )

            self.post_3d_menu.update_column()

            is_left_visible = self.ui.is_left_column_visible()
            if not is_left_visible:
                self.ui.toggle_left_column()
            self.post_3d_menu.plotter.reparent_to_placeholder(self.post_3d_menu.class_name)

    def help_menu_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()
        self.ui.left_menu.select_only_one(selected_menu.objectName())
        if menu_name == "help_menu":
            selected_menu.set_active(True)
            self.ui.set_page(self.help_menu.plot_design_menu_widget)

            self.ui.set_left_column_menu(
                menu=self.help_menu.plot_design_column_widget,
                title="Help",
                icon_path=self.ui.images_load.icon_path("help.svg"),
            )

            is_left_visible = self.ui.is_left_column_visible()
            if not is_left_visible:
                self.ui.toggle_left_column()

    def close_event(self, event):  # pragma: no cover
        self.home_menu.plotter.pv_backend.close()
        event.accept()


def run_frontend(backend_url="", backend_port=0, app=None):  # pragma: no cover
    if backend_url:
        properties.backend_url = backend_url
    if backend_port:
        properties.backend_port = backend_port

    run_separately = False

    if not app:
        run_separately = True
        app = QApplication(sys.argv)

    window = ApplicationWindow()
    window.show()
    app.processEvents()
    if run_separately:
        sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    run_frontend()
