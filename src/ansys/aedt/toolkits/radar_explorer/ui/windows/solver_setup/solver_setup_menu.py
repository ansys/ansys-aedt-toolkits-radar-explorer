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

from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QWidget

from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.toolkits.common.ui.utils.widgets import PyIconButton
from ansys.aedt.toolkits.radar_explorer.ui.models import properties
from ansys.aedt.toolkits.radar_explorer.ui.windows.common_windows_utils import CommonWindowUtilsRCS
from ansys.aedt.toolkits.radar_explorer.ui.windows.solver_setup.solver_column import Ui_LeftColumn


class SolveThread(QThread):
    finished_signal = Signal(bool)

    def __init__(self, app):
        super().__init__()
        self.main_window = app.main_window
        self.metadata_file = []

    def run(self):
        if not self.main_window.solver_setup_menu.solve_interactive.isChecked():
            # Open progress bar
            is_progress_visible = self.main_window.ui.is_progress_visible()
            if not is_progress_visible:
                self.main_window.ui.toggle_progress()

        new_props = self.main_window.rcs_setup()
        if not new_props:
            self.main_window.ui.update_logger("Setup could not be created")
            self.finished_signal.emit(False)

        success = self.main_window.analyze()

        if not success:
            self.finished_signal.emit(success)

        polarization_combinations = {
            "vv": ["IncWaveVpol", "ComplexMonostaticRCSTheta"],
            "vh": ["IncWaveHpol", "ComplexMonostaticRCSTheta"],
            "hv": ["IncWaveVpol", "ComplexMonostaticRCSPhi"],
            "hh": ["IncWaveHpol", "ComplexMonostaticRCSPhi"],
        }

        for excitation, expression in polarization_combinations.values():
            self.metadata_file.append(self.main_window.export_rcs(excitation, expression))
            if not self.metadata_file:
                self.finished_signal.emit(False)

        if not self.main_window.solver_setup_menu.solve_interactive.isChecked():
            self.main_window.release_desktop()

        self.finished_signal.emit(self.metadata_file)


class SolverSetupMenu(object):
    def __init__(self, main_window):
        # General properties
        self.main_window = main_window
        self.ui = main_window.ui

        self.app_color = self.main_window.ui.themes["app_color"]
        self.title_size = properties.font["title_size"]
        self.combo_size = properties.font["combo_size"]
        self.active_color = self.app_color["text_active"]
        self.background_color = self.app_color["dark_three"]
        self.background_color_title = self.app_color["dark_four"]

        # Add left column
        new_column_widget = QWidget()
        new_ui = Ui_LeftColumn()
        new_ui.setupUi(new_column_widget)
        self.ui.left_column.menus.menus.addWidget(new_column_widget)
        self.solver_setup_column_widget = new_column_widget
        self.solver_setup_column_vertical_layout = new_ui.solver_setup_vertical_layout

        self.solver_setup_combo_widget = None
        self.solver_setup_label = None
        self.solver_setup_combobox = None

        self.line1 = None

        self.ray_density_widget = None
        self.ray_density_label = None
        self.ray_density_textbox = None

        self.num_bounces_widget = None
        self.num_bounces_label = None
        self.num_bounces_textbox = None

        self.line2 = None

        self.fast_freq_label = None
        self.toggle = None

        self.cores_widget = None
        self.cores_label = None
        self.cores_textbox = None

        self.ptd_utd_label = None
        self.ptd_utd = None

        self.solve_interactive_label = None
        self.solve_interactive = None

        self.solve_button_layout = None
        self.solve_button = None

        self.post_3d_settings_label = None
        self.post_3d_setting_icon = None
        self.line3 = None

        # Thread
        self.solve_thread = None

        # Common RCS Utils
        self.rcs_utils = CommonWindowUtilsRCS(self.main_window.ui.themes)

    def setup(self):
        row_returns = self.ui.add_combobox(
            self.solver_setup_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Solve Mode",
            combobox_list=["Monostatic"],
            font_size=self.combo_size,
        )
        self.solver_setup_combo_widget = row_returns[0]
        self.solver_setup_label = row_returns[1]
        self.solver_setup_combobox = row_returns[2]

        self.line1 = self.ui.add_vertical_line(
            self.solver_setup_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.solver_setup_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Ray Density",
            value=properties.radar_explorer.ray_density,
            unit="",
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )
        self.ray_density_widget = row_returns[0]
        self.ray_density_label = row_returns[1]
        self.ray_density_textbox = row_returns[2]

        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.solver_setup_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Num. Bounces",
            value=properties.radar_explorer.bounces,
            unit="",
            val_type=int,
            precision=0,
            font_size=self.combo_size,
        )
        self.num_bounces_widget = row_returns[0]
        self.num_bounces_label = row_returns[1]
        self.num_bounces_textbox = row_returns[2]

        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.solver_setup_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Cores",
            value=properties.radar_explorer.cores,
            unit="",
            val_type=int,
            precision=0,
            font_size=self.combo_size,
        )
        self.cores_widget = row_returns[0]
        self.cores_label = row_returns[1]
        self.cores_textbox = row_returns[2]

        row_returns = self.ui.add_toggle(
            self.solver_setup_column_vertical_layout,
            height=30,
            width=[135, 180, 0],
            label=["Fast Freq. Looping", " "],
            font_size=self.combo_size,
            bg_color=self.app_color["label_off"],
            active_color=self.app_color["label_on"],
            text_color_on=self.app_color["text_foreground"],
            text_color_off=self.app_color["text_foreground"],
            show_on_off=True,
        )
        self.ui.left_column.menus.fast_freq_loop_row = row_returns[0]
        self.fast_freq_label = row_returns[1]
        self.toggle = row_returns[2]
        self.toggle.setChecked(properties.radar_explorer.fast_frequency_looping)

        row_returns = self.ui.add_toggle(
            self.solver_setup_column_vertical_layout,
            height=30,
            width=[155, 180, 0],
            label=["PTD correction and UTD Rays", " "],
            font_size=self.combo_size,
            bg_color=self.app_color["label_off"],
            active_color=self.app_color["label_on"],
            text_color_on=self.app_color["text_foreground"],
            text_color_off=self.app_color["text_foreground"],
            show_on_off=True,
        )
        self.ui.left_column.menus.ptd_utd_row = row_returns[0]
        self.ptd_utd_label = row_returns[1]
        self.ptd_utd = row_returns[2]
        self.ptd_utd.setChecked(properties.radar_explorer.ptd_utd)

        row_returns = self.ui.add_toggle(
            self.solver_setup_column_vertical_layout,
            height=30,
            width=[135, 180, 0],
            label=["Interactive", " "],
            font_size=self.combo_size,
            bg_color=self.app_color["label_off"],
            active_color=self.app_color["label_on"],
            text_color_on=self.app_color["text_foreground"],
            text_color_off=self.app_color["text_foreground"],
            show_on_off=True,
        )
        self.ui.left_column.menus.solve_interactive_row = row_returns[0]
        self.solve_interactive_label = row_returns[1]
        self.solve_interactive = row_returns[2]
        self.solve_interactive.setChecked(properties.radar_explorer.solve_interactive)

        self.line2 = self.ui.add_vertical_line(
            self.solver_setup_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        row_returns = self.ui.add_n_buttons(
            self.solver_setup_column_vertical_layout,
            num_buttons=1,
            height=40,
            width=[180],
            text=["Solve"],
            font_size=self.title_size,
        )

        self.solve_button_layout = row_returns[0]
        self.solve_button = row_returns[1]
        self.solve_button_layout.addWidget(self.solve_button)
        self.solve_button.setEnabled(False)
        self.solve_button.clicked.connect(self.solve)

        self.line3 = self.ui.add_vertical_line(
            self.solver_setup_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        self.post_3d_settings_setup()

    def solve(self):
        # Start a separate thread for the backend call
        self.solve_thread = SolveThread(app=self)
        self.solve_thread.finished_signal.connect(self.solve_finished)
        msg = "Creating and analyzing setup"
        self.ui.update_logger(msg)
        self.ui.update_progress(50)

        self.solve_thread.start()

        self.main_window.mode_select_menu.save_status()
        self.main_window.mode_select_menu.set_options_enabled(False)
        self.main_window.incident_wave_menu.save_status()
        self.main_window.incident_wave_menu.set_options_enabled(False)
        self.save_status()
        self.set_options_enabled(False)
        return True

    def solve_finished(self):
        self.main_window.home_menu.plotter.rotation_active = False
        self.main_window.home_menu.reset_scene()
        if self.solve_thread.metadata_file:
            for metadata_file in self.solve_thread.metadata_file:
                self.main_window.home_menu.load_rcs_metadatada(metadata_file)
                metadata_file_relative = Path(metadata_file).name
                properties.radar_explorer.metadata_files.append(metadata_file_relative)

            dir_name = Path(self.solve_thread.metadata_file[0]).parent
            configuration_file = dir_name / "analysis_setup.json"
            configuration_str = properties.radar_explorer.model_dump_json(
                exclude=["all_scene_actors", "reports"], indent=4
            )

            with configuration_file.open("w", encoding="utf-8") as f:
                f.write(configuration_str)

            # pickup the last data, and populate the post proc windows:
            rcs_objects = properties.radar_explorer.all_scene_actors["plotter"]
            if len(rcs_objects.values()) > 1:
                raise Exception("Not tested for multiple solutions")
            last_data = next(reversed(rcs_objects.values()), None)
            CommonWindowUtilsRCS.set_visible_post_proc(self, True, last_data)
            self.ui.update_logger("Design solved")
            self.ui.update_progress(100)
        else:
            self.ui.update_logger("Analysis failed")
            self.ui.update_progress(100)
            return False

    def set_options_enabled(self, enabled: bool = False):
        self.ray_density_textbox.setEnabled(enabled)
        self.ray_density_textbox.blocked = not enabled

        self.num_bounces_textbox.setEnabled(enabled)
        self.num_bounces_textbox.blocked = not enabled

        self.toggle.setEnabled(enabled)
        self.ptd_utd.setEnabled(enabled)
        self.solve_interactive.setEnabled(enabled)
        self.cores_textbox.setEnabled(enabled)
        self.cores_textbox.blocked = not enabled

        self.solve_button.setEnabled(enabled)

    def save_status(self):
        properties.radar_explorer.ray_density = f"{self.ray_density_textbox.value}{self.ray_density_textbox.unit}"
        properties.radar_explorer.bounces = f"{self.num_bounces_textbox.value}"
        properties.radar_explorer.fast_frequency_looping = self.toggle.isChecked()
        properties.radar_explorer.ptd_utd = self.ptd_utd.isChecked()
        properties.radar_explorer.solve_interactive = self.solve_interactive.isChecked()
        properties.radar_explorer.cores = f"{self.cores_textbox.value}"

    def load_status(self):
        ray_density = Quantity(properties.radar_explorer.ray_density)
        self.ray_density_textbox.precision = properties.radar_explorer.precision
        self.ray_density_textbox.set_value_unit_text(ray_density.value, ray_density.unit)

        bounces = Quantity(properties.radar_explorer.bounces)
        self.num_bounces_textbox.precision = properties.radar_explorer.precision
        self.num_bounces_textbox.set_value_unit_text(bounces.value, bounces.unit)

        self.toggle.setChecked(properties.radar_explorer.fast_frequency_looping)

        self.ptd_utd.setChecked(properties.radar_explorer.ptd_utd)
        self.solve_interactive.setChecked(properties.radar_explorer.solve_interactive)

        cores = Quantity(properties.radar_explorer.cores)
        self.cores_textbox.precision = properties.radar_explorer.precision
        self.cores_textbox.set_value_unit_text(cores.value, cores.unit)

    def post_3d_settings_setup(self):
        layout_row_obj = QHBoxLayout()
        self.solver_setup_column_vertical_layout.addLayout(layout_row_obj)

        self.post_3d_settings_label = QLabel("3D Settings")
        self.post_3d_settings_label.setStyleSheet(
            f"font-size: {self.title_size}pt; color: {self.active_color};font-weight: bold;"
        )
        layout_row_obj.addWidget(self.post_3d_settings_label)

        theme = self.main_window.ui.themes
        self.post_3d_setting_icon = PyIconButton(
            icon_path=self.ui.images_load.icon_path("icon_settings.svg"),
            tooltip_text=None,
            width=40,
            height=40,
            radius=10,
            dark_one=theme["app_color"]["dark_one"],
            icon_color=theme["app_color"]["icon_color"],
            icon_color_hover=theme["app_color"]["icon_hover"],
            icon_color_pressed=theme["app_color"]["icon_active"],
            icon_color_active=theme["app_color"]["icon_active"],
            bg_color=theme["app_color"]["dark_one"],
            bg_color_hover=theme["app_color"]["dark_three"],
            bg_color_pressed=theme["app_color"]["pink"],
        )
        self.post_3d_setting_icon.setMinimumHeight(40)
        layout_row_obj.addWidget(self.post_3d_setting_icon)
        self.post_3d_setting_icon.clicked.connect(self.main_window.home_menu.model_3d_settings)
