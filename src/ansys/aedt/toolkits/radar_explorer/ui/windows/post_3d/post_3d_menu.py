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

import tempfile

from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from ansys.aedt.core.generic.numbers_utils import Quantity
from scipy.interpolate import RegularGridInterpolator
from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.utils import unit_converter_rcs
from ansys.aedt.toolkits.common.ui.utils.widgets import PyIconButton
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter
from ansys.aedt.toolkits.radar_explorer.ui.models import properties
from ansys.aedt.toolkits.radar_explorer.ui.windows.post_3d.post_3d_column import Ui_LeftColumn
from ansys.aedt.toolkits.radar_explorer.ui.windows.post_3d.post_3d_page import Ui_Plot_Design
from ansys.aedt.toolkits.radar_explorer.ui.windows.common_windows_utils import CommonWindowUtilsRCS


class Plot3DThread(QThread):
    finished_signal = Signal(bool)

    def __init__(self, app):
        super().__init__()
        self.main_window = app.main_window

    def run(self):
        solution = self.main_window.post_3d_menu.solution_combobox.currentText()

        category = self.main_window.post_3d_menu.category_combobox.currentText()
        aspect_range_combobox = self.main_window.post_3d_menu.aspect_range_combobox.currentText()
        theta = self.main_window.post_3d_menu.theta_combobox.currentText()
        phi = self.main_window.post_3d_menu.phi_combobox.currentText()
        freq = self.main_window.post_3d_menu.freq_combobox.currentText()

        plot_type = self.main_window.post_3d_menu.plot_type_combobox.currentText()
        polarization = self.main_window.post_3d_menu.polarization_combobox.currentText()
        window = self.main_window.post_3d_menu.window_combobox.currentText()
        upsample = self.main_window.post_3d_menu.upsample_textbox.text()
        upsample_az = self.main_window.post_3d_menu.upsample_az_textbox.text()
        upsample_el = self.main_window.post_3d_menu.upsample_el_textbox.text()
        function_expression = self.main_window.post_3d_menu.function_combobox.currentText()
        plane_cut = self.main_window.post_3d_menu.plane_cut_combobox.currentText()

        plane_offset = unit_converter_rcs(
            value=self.main_window.post_3d_menu.plane_offset_textbox.text_full_precision(),
            new_units=properties.radar_explorer.model_units
        )

        interpolation = self.main_window.post_3d_menu.interpolation_combobox.currentText()
        extrapolate = self.main_window.post_3d_menu.extrapolate.isChecked()
        gridsize = self.main_window.post_3d_menu.gridsize_combobox.currentText()

        data: MonostaticRCSPlotter = None

        if solution != "No solution":
            data = properties.radar_explorer.all_scene_actors["plotter"][solution][polarization]

        if data:
            data.num_contours = properties.radar_explorer.num_contours
            if function_expression == "dB":
                function_expression = "dB20"
            if function_expression == "phase":
                function_expression = "ang_deg"
            data.rcs_data.data_conversion_function = function_expression
            data.clear_scene()
            if category == "RCS":
                data.rcs_data.frequency = float(freq)
                data.add_rcs()

                if solution not in properties.radar_explorer.all_scene_actors["results"]:
                    properties.radar_explorer.all_scene_actors["results"][solution] = {}

                for report_name, rcs_plot in data.all_scene_actors["results"]["rcs"].items():
                    cont = 1
                    while report_name in properties.radar_explorer.all_scene_actors["results"][solution]:
                        report_name = f"rcs_{cont}"
                        cont += 1
                    properties.radar_explorer.all_scene_actors["results"][solution][report_name] = rcs_plot

            elif category == "Range Profile":
                data.rcs_data.incident_wave_phi = float(phi)
                data.rcs_data.incident_wave_theta = float(theta)
                data.rcs_data.window = window
                data.rcs_data.window_size = int(upsample)

                data.add_range_profile(plot_type=plot_type)

                if solution not in properties.radar_explorer.all_scene_actors["results"]:
                    properties.radar_explorer.all_scene_actors["results"][solution] = {}

                for report_name, rcs_plot in data.all_scene_actors["results"]["range_profile"].items():
                    cont = 1
                    while report_name in properties.radar_explorer.all_scene_actors["results"][solution]:
                        report_name = f"range_profile_{cont}"
                        cont += 1
                    properties.radar_explorer.all_scene_actors["results"][solution][report_name] = rcs_plot

            elif category == "Waterfall":
                data.rcs_data.aspect_range = aspect_range_combobox
                data.rcs_data.incident_wave_phi = float(phi)
                data.rcs_data.incident_wave_theta = float(theta)
                data.rcs_data.window = window
                data.rcs_data.window_size = int(upsample)

                data.add_waterfall()

                if solution not in properties.radar_explorer.all_scene_actors["results"]:
                    properties.radar_explorer.all_scene_actors["results"][solution] = {}

                for report_name, rcs_plot in data.all_scene_actors["results"]["waterfall"].items():
                    cont = 1
                    while report_name in properties.radar_explorer.all_scene_actors["results"][solution]:
                        report_name = f"waterfall_{cont}"
                        cont += 1
                    properties.radar_explorer.all_scene_actors["results"][solution][report_name] = rcs_plot

            elif category == "2D ISAR":
                data.rcs_data.aspect_range = aspect_range_combobox
                data.rcs_data.incident_wave_phi = float(phi)
                data.rcs_data.incident_wave_theta = float(theta)
                data.rcs_data.window = window
                data.rcs_data.upsample_range = int(upsample)
                data.rcs_data.upsample_azimuth = int(upsample_az)
                data.rcs_data.upsample_elevation = int(upsample_el)
                data.rcs_data.data_conversion_function = function_expression
                data.rcs_data.interpolation = interpolation
                data.rcs_data.extrapolate = extrapolate
                data.rcs_data.gridsize = gridsize

                data.add_isar_2d(plot_type=plot_type)

                if solution not in properties.radar_explorer.all_scene_actors["results"]:
                    properties.radar_explorer.all_scene_actors["results"][solution] = {}

                for report_name, rcs_plot in data.all_scene_actors["results"]["isar_2d"].items():
                    cont = 1
                    while report_name in properties.radar_explorer.all_scene_actors["results"][solution]:
                        report_name = f"isar_2d_{cont}"
                        cont += 1
                    properties.radar_explorer.all_scene_actors["results"][solution][report_name] = rcs_plot

            elif category == "3D ISAR":
                data.rcs_data.window = window
                data.rcs_data.upsample_range = int(upsample)
                data.rcs_data.upsample_azimuth = int(upsample_az)
                data.rcs_data.upsample_elevation = int(upsample_el)
                data.rcs_data.data_conversion_function = function_expression
                data.rcs_data.interpolation = interpolation
                data.rcs_data.extrapolate = extrapolate
                data.rcs_data.gridsize = gridsize

                data.add_isar_3d(plot_type=plot_type, plane_cut=plane_cut, plane_offset=float(plane_offset))

                if solution not in properties.radar_explorer.all_scene_actors["results"]:
                    properties.radar_explorer.all_scene_actors["results"][solution] = {}

                for report_name, rcs_plot in data.all_scene_actors["results"]["isar_3d"].items():
                    cont = 1
                    while report_name in properties.radar_explorer.all_scene_actors["results"][solution]:
                        report_name = f"isar_2d_{cont}"
                        cont += 1
                    properties.radar_explorer.all_scene_actors["results"][solution][report_name] = rcs_plot

        self.finished_signal.emit(True)


class Post3DMenu(object):
    def __init__(self, main_window):
        # General properties
        self.class_name = "Post3DMenu"
        self.main_window = main_window
        self.ui = main_window.ui
        self.temp_folder = tempfile.mkdtemp()

        self.dark_mode = True if "dark" in self.main_window.ui.themes["theme_name"] else False
        self.app_color = self.main_window.ui.themes["app_color"]
        self.title_size = properties.font["title_size"]
        self.active_color = self.app_color["text_active"]
        self.background_color = self.app_color["dark_three"]
        self.background_color_title = self.app_color["dark_four"]
        self.combo_size = self.main_window.properties.font["combo_size"]

        # Add page
        post_3d_menu_index = self.ui.add_page(Ui_Plot_Design)
        self.ui.load_pages.pages.setCurrentIndex(post_3d_menu_index)
        self.post_3d_menu_widget = self.ui.load_pages.pages.currentWidget()

        # Add left column
        new_column_widget = QWidget()
        new_ui = Ui_LeftColumn()
        new_ui.setupUi(new_column_widget)
        self.ui.left_column.menus.menus.addWidget(new_column_widget)
        self.post_3d_column_widget = new_column_widget
        self.post_3d_column_vertical_layout = new_ui.plot_design_vertical_layout

        # Specific properties
        self.post_3d_layout = self.post_3d_menu_widget.findChild(QVBoxLayout, "plot_design_layout")

        # Solution combobox
        self.solution_combo_widget = None
        self.solution_label = None
        self.solution_combobox = None

        # Category combobox
        self.category_combo_widget = None
        self.category_label = None
        self.category_combobox = None

        self.line1 = None

        # Primary sweep
        self.primary_sweep_combo_widget = None
        self.primary_sweep_label = None
        self.primary_sweep_combobox = None

        # Plane selection for 2D ISAR
        self.aspect_range_combo_widget = None
        self.aspect_range_label = None
        self.aspect_range_combobox = None

        # Incident wave theta
        self.theta_combo_widget = None
        self.theta_label = None
        self.theta_combobox = None

        # Incident wave phi
        self.phi_combo_widget = None
        self.phi_label = None
        self.phi_combobox = None

        # Freq
        self.freq_combo_widget = None
        self.freq_label = None
        self.freq_combobox = None

        self.line2 = None

        # Polarization
        self.polarization_combo_widget = None
        self.polarization_label = None
        self.polarization_combobox = None

        # Plot type
        self.plot_type_combo_widget = None
        self.plot_type_label = None
        self.plot_type_combobox = None

        # Function
        self.function_combo_widget = None
        self.function_label = None
        self.function_combobox = None

        # Gridsize
        self.gridsize_combo_widget = None
        self.gridsize_label = None
        self.gridsize_combobox = None

        # Interpolation
        self.interpolation_combo_widget = None
        self.interpolation_label = None
        self.interpolation_combobox = None

        # Extrapolation switch
        self.extrapolate_label = None
        self.extrapolate = None

        # Window
        self.window_combo_widget = None
        self.window_label = None
        self.window_combobox = None

        # Upsample
        self.upsample_text_widget = None
        self.upsample_label = None
        self.upsample_textbox = None

        # Upsample Az
        self.upsample_az_text_widget = None
        self.upsample_az_label = None
        self.upsample_az_textbox = None

        # Upsample El
        self.upsample_el_text_widget = None
        self.upsample_el_label = None
        self.upsample_el_textbox = None

        # Plane cut
        self.plane_cut_combo_widget = None
        self.plane_cut_label = None
        self.plane_cut_combobox = None

        # Plane offset
        self.plane_offset_text_widget = None
        self.plane_offset_label = None
        self.plane_offset_textbox = None

        self.line3 = None
        self.line5 = None

        # Button
        self.post_3d_button_layout = None
        self.post_3d_button = None
        self.result_combobox = None
        self.result_combo_widget = None
        self.result_label = None
        self.result_3d_tabs = {}
        self.result_widget = {}

        # Settings
        self.line4 = None
        self.post_3d_settings_label = None
        self.post_3d_setting_icon = None

        self.post_3d_loaded_tree = None

        self.post_3d_delete_button_layout = None
        self.post_3d_delete_button = None

        self.projection_menu_layout = None
        self.projection_menu_label = None
        self.projection_menu = None

        # Menu
        self.plotter = self.main_window.home_menu.plotter
        self.post_3d_loaded_tree = None
        self.plot_thread = None

        # Common RCS Utils
        self.rcs_utils = CommonWindowUtilsRCS(self.main_window.ui.themes)

    def setup(self):
        # Solution combobox
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[75, 180],
            label="Solution",
            combobox_list=["No solution"],
            font_size=self.combo_size,
        )

        self.solution_combo_widget = row_returns[0]
        self.solution_label = row_returns[1]
        self.solution_combobox = row_returns[2]
        self.solution_combobox.currentIndexChanged.connect(lambda: self.update_solution())

        # Category combobox
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[75, 180],
            label="Category",
            combobox_list=["RCS", "Range Profile", "Waterfall", "2D ISAR", "3D ISAR"],
            font_size=self.combo_size,
        )

        self.category_combo_widget = row_returns[0]
        self.category_label = row_returns[1]
        self.category_combobox = row_returns[2]
        self.category_combobox.currentIndexChanged.connect(lambda: self.update_column())

        self.line1 = self.ui.add_vertical_line(
            self.post_3d_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        # Primary sweep
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Primary Sweep",
            combobox_list=["Frequency", "Theta", "Phi"],
            font_size=self.combo_size,
        )

        self.primary_sweep_combo_widget = row_returns[0]
        self.primary_sweep_label = row_returns[1]
        self.primary_sweep_combobox = row_returns[2]
        self.primary_sweep_combobox.currentIndexChanged.connect(lambda: self.update_column())

        # Aspect range
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Plane Selection",
            combobox_list=["Horizontal", "Vertical"],
            font_size=self.combo_size,
        )

        self.aspect_range_combo_widget = row_returns[0]
        self.aspect_range_label = row_returns[1]
        self.aspect_range_combobox = row_returns[2]
        self.aspect_range_label.setVisible(False)
        self.aspect_range_combobox.setVisible(False)
        self.aspect_range_combobox.currentIndexChanged.connect(lambda: self.update_column())

        # Incident wave theta
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="IWave Theta",
            combobox_list=["None"],
            font_size=self.combo_size,
        )

        self.theta_combo_widget = row_returns[0]
        self.theta_label = row_returns[1]
        self.theta_combobox = row_returns[2]

        # Incident wave phi
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="IWave Phi",
            combobox_list=["None"],
            font_size=self.combo_size,
        )

        self.phi_combo_widget = row_returns[0]
        self.phi_label = row_returns[1]
        self.phi_combobox = row_returns[2]

        # Freq
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Frequency",
            combobox_list=["None"],
            font_size=self.combo_size,
        )

        self.freq_combo_widget = row_returns[0]
        self.freq_label = row_returns[1]
        self.freq_combobox = row_returns[2]

        self.line2 = self.ui.add_vertical_line(
            self.post_3d_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        # Receive polarization
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Polarization",
            combobox_list=["None"],
            font_size=self.combo_size,
        )

        self.polarization_combo_widget = row_returns[0]
        self.polarization_label = row_returns[1]
        self.polarization_combobox = row_returns[2]
        self.polarization_combobox.currentIndexChanged.connect(lambda: self.update_polarization())

        # Plot type
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Plot Type",
            combobox_list=["Line"],
            font_size=self.combo_size,
        )

        self.plot_type_combo_widget = row_returns[0]
        self.plot_type_label = row_returns[1]
        self.plot_type_combobox = row_returns[2]
        self.plot_type_combobox.currentIndexChanged.connect(lambda: self.update_plot_type())

        # Function
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Function",
            combobox_list=["dB", "abs", "real", "imag", "phase"],
            font_size=self.combo_size,
        )

        self.function_combo_widget = row_returns[0]
        self.function_label = row_returns[1]
        self.function_combobox = row_returns[2]

        self.line5 = self.ui.add_vertical_line(
            self.post_3d_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        # Gridsize
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Grid Frequency",
            combobox_list=["Middle", "Inside", "Outside"],
            font_size=self.combo_size,
        )

        self.gridsize_combo_widget = row_returns[0]
        self.gridsize_label = row_returns[1]
        self.gridsize_combobox = row_returns[2]

        # Interpolation
        # pchip is not compatible with complex data
        interp_methods = [i for i in RegularGridInterpolator._ALL_METHODS if i != "pchip"]
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Interpolation",
            combobox_list=interp_methods,
            font_size=self.combo_size,
        )

        self.interpolation_combo_widget = row_returns[0]
        self.interpolation_label = row_returns[1]
        self.interpolation_combobox = row_returns[2]

        # Extrapolation switch
        row_returns = self.ui.add_toggle(
            self.post_3d_column_vertical_layout,
            height=30,
            width=[135, 180, 0],
            label=["Extrapolate", ""],
            font_size=self.combo_size,
            bg_color=self.app_color["label_off"],
            active_color=self.app_color["label_on"],
            text_color_on=self.app_color["text_foreground"],
            text_color_off=self.app_color["text_foreground"],
            show_on_off=True,
        )
        self.ui.left_column.menus.extrapolate_row = row_returns[0]
        self.extrapolate_label = row_returns[1]
        self.extrapolate = row_returns[2]
        self.extrapolate.setChecked(True)

        self.line6 = self.ui.add_vertical_line(
            self.post_3d_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        # Window
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="FFT Window",
            combobox_list=["Flat", "Hann", "Hamming"],
            font_size=self.combo_size,
        )

        self.window_combo_widget = row_returns[0]
        self.window_label = row_returns[1]
        self.window_combobox = row_returns[2]

        # Upsample
        row_returns = self.ui.add_textbox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Num Pix Rng",
            initial_text="512",
            font_size=self.combo_size,
        )

        self.upsample_text_widget = row_returns[0]
        self.upsample_label = row_returns[1]
        self.upsample_textbox = row_returns[2]

        # Upsample Az
        row_returns = self.ui.add_textbox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Num Pix XRng (Az)",
            initial_text="64",
            font_size=self.combo_size,
        )

        self.upsample_az_text_widget = row_returns[0]
        self.upsample_az_label = row_returns[1]
        self.upsample_az_textbox = row_returns[2]

        # Upsample El
        row_returns = self.ui.add_textbox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Num Pix XRng (El)",
            initial_text="32",
            font_size=self.combo_size,
        )

        self.upsample_el_text_widget = row_returns[0]
        self.upsample_el_label = row_returns[1]
        self.upsample_el_textbox = row_returns[2]

        # Plane cut
        row_returns = self.ui.add_combobox(
            self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Plane Cut",
            combobox_list=["XY", "XZ", "YZ"],
            font_size=self.combo_size,
        )

        self.plane_cut_combo_widget = row_returns[0]
        self.plane_cut_label = row_returns[1]
        self.plane_cut_combobox = row_returns[2]

        # Plane offset
        plane_offset_default = Quantity("0.0m")
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.post_3d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Plane Offset",
            value=plane_offset_default.value,
            val_type=float,
            precision=properties.radar_explorer.precision,
            unit=plane_offset_default.unit,
            font_size=self.combo_size,
        )
        self.plane_offset_text_widget = row_returns[0]
        self.plane_offset_label = row_returns[1]
        self.plane_offset_textbox = row_returns[2]

        self.line3 = self.ui.add_vertical_line(
            self.post_3d_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        # Plot design
        row_returns = self.ui.add_n_buttons(
            self.post_3d_column_vertical_layout,
            num_buttons=1,
            height=40,
            width=[200],
            text=["Plot"],
            font_size=self.combo_size,
        )

        self.post_3d_button_layout = row_returns[0]
        self.post_3d_button = row_returns[1]
        self.post_3d_button_layout.addWidget(self.post_3d_button)
        self.post_3d_button.clicked.connect(self.post_3d_button_clicked)

        self.line4 = self.ui.add_vertical_line(
            self.post_3d_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        self.post_3d_settings_setup()

        # Page
        self.initialize_plotter()
        self.on_tab_changed()

    def on_tab_changed(self):
        if self.main_window.ui.get_selected_menu() == "post_3d_menu":
            self.plotter.reparent_to_placeholder(self.class_name)

    def initialize_plotter(self):
        self.plotter.add_to_window(self.class_name, self.post_3d_layout)

    def update_solution(self):
        solution = self.solution_combobox.currentText()
        # Update polarization for solution
        self.polarization_combobox.blockSignals(True)
        self.polarization_combobox.clear()
        polarizations = list(properties.radar_explorer.all_scene_actors["plotter"][solution].keys())
        self.polarization_combobox.addItems(polarizations)
        self.polarization_combobox.blockSignals(False)

        self.update_polarization()

        # initialize aspect range used in 2D ISAR
        self.aspect_range_combobox.blockSignals(True)
        self.aspect_range_combobox.clear()
        if self.theta_combobox.count() > 1 and self.phi_combobox.count() > 1:
            self.aspect_range_combobox.addItems(["Horizontal", "Vertical"])
            self.aspect_range_combobox.setEnabled(True)
        elif self.theta_combobox.count() > 1:
            self.aspect_range_combobox.addItems(["Vertical"])
            self.aspect_range_combobox.setEnabled(False)
        elif self.phi_combobox.count() > 1:
            self.aspect_range_combobox.addItems(["Horizontal"])
            self.aspect_range_combobox.setEnabled(False)
        else:
            raise ValueError("No theta or phi available for 2D ISAR plot")
        self.aspect_range_combobox.blockSignals(False)

        # initialize primary sweep used in RCS
        # TODO: Issue 124: let's design what we want to plot in 3D RCS plot. We might consider
        # to plot "Frequency-Theta" and "Frequency-Phi" like waterfall
        self.primary_sweep_combobox.blockSignals(True)
        self.primary_sweep_combobox.clear()
        # self.primary_sweep_combobox.addItems(["Theta-Phi","Frequency-Theta", "Frequency-Phi"])
        self.primary_sweep_combobox.addItems(["Theta-Phi"])
        self.primary_sweep_combobox.setEnabled(False)
        self.primary_sweep_combobox.blockSignals(False)

    # Column
    def update_column(self):
        # Populate solutions if new one is added
        if (self.solution_combobox.currentText() == "No solution"
                or self.solution_combobox.count() != len(properties.radar_explorer.solution_names)):
            self.solution_combobox.blockSignals(True)
            self.solution_combobox.clear()
            solutions = properties.radar_explorer.solution_names
            self.solution_combobox.addItems(solutions)
            self.solution_combobox.setCurrentIndex(len(solutions) - 1)
            self.solution_combobox.blockSignals(False)
            # Select the last solution and populate the rest
            self.update_solution()

        category = self.category_combobox.currentText()
        if category == "RCS":
            self.line1.setVisible(True)
            self.line5.setVisible(False)
            self.line6.setVisible(False)
            self.aspect_range_combobox.setVisible(False)
            self.aspect_range_label.setVisible(False)

            self.primary_sweep_combobox.setVisible(True)
            self.primary_sweep_label.setVisible(True)
            if self.primary_sweep_combobox.currentText() == "Theta-Phi":
                self.freq_combobox.setVisible(True)
                self.freq_label.setVisible(True)
                self.phi_combobox.setVisible(False)
                self.phi_label.setVisible(False)
                self.theta_combobox.setVisible(False)
                self.theta_label.setVisible(False)
            elif self.primary_sweep_combobox.currentText() == "Frequency-Theta":
                self.freq_combobox.setVisible(False)
                self.freq_label.setVisible(False)
                self.phi_combobox.setVisible(True)
                self.phi_label.setVisible(True)
                self.theta_combobox.setVisible(False)
                self.theta_label.setVisible(False)
            elif self.primary_sweep_combobox.currentText() == "Frequency-Phi":
                self.freq_combobox.setVisible(False)
                self.freq_label.setVisible(False)
                self.phi_combobox.setVisible(False)
                self.phi_label.setVisible(False)
                self.theta_combobox.setVisible(True)
                self.theta_label.setVisible(True)

            self.polarization_combobox.setVisible(True)
            self.polarization_label.setVisible(True)
            self.plot_type_combobox.setVisible(True)
            self.plot_type_label.setVisible(True)
            self.function_combobox.setVisible(True)
            self.function_label.setVisible(True)

            self.window_combobox.setVisible(False)
            self.window_label.setVisible(False)
            self.upsample_textbox.setVisible(False)
            self.upsample_label.setVisible(False)
            self.upsample_az_textbox.setVisible(False)
            self.upsample_az_label.setVisible(False)
            self.upsample_el_textbox.setVisible(False)
            self.upsample_el_label.setVisible(False)
            self.plane_cut_combobox.setVisible(False)
            self.plane_cut_label.setVisible(False)
            self.plane_offset_textbox.setVisible(False)
            self.plane_offset_label.setVisible(False)

            self.interpolation_combobox.setVisible(False)
            self.interpolation_label.setVisible(False)
            self.extrapolate.setVisible(False)
            self.extrapolate_label.setVisible(False)
            self.gridsize_combobox.setVisible(False)
            self.gridsize_label.setVisible(False)

            self.plot_type_combobox.clear()
            self.plot_type_combobox.addItems(["Line"])

        elif category == "Range Profile" or category == "Waterfall":
            self.line1.setVisible(True)
            self.line5.setVisible(False)
            self.line6.setVisible(True)
            if category == "Range Profile":
                self.aspect_range_combobox.setVisible(False)
                self.aspect_range_label.setVisible(False)
                self.theta_combobox.setVisible(True)
                self.theta_label.setVisible(True)
                self.phi_combobox.setVisible(True)
                self.phi_label.setVisible(True)
            else:
                self.aspect_range_label.setVisible(True)
                self.aspect_range_combobox.setVisible(True)
                if self.aspect_range_combobox.currentText() == "Horizontal":
                    self.theta_label.setVisible(True)
                    self.theta_combobox.setVisible(True)
                    self.theta_combobox.setCurrentIndex(self.theta_combobox.count() // 2)
                    self.phi_combobox.setVisible(False)
                    self.phi_label.setVisible(False)
                elif self.aspect_range_combobox.currentText() == "Vertical":
                    self.theta_label.setVisible(False)
                    self.theta_combobox.setVisible(False)
                    self.phi_combobox.setVisible(True)
                    self.phi_label.setVisible(True)
                    self.phi_combobox.setCurrentIndex(self.phi_combobox.count() // 2)
            self.freq_combobox.setVisible(False)
            self.freq_label.setVisible(False)

            self.primary_sweep_combobox.setVisible(False)
            self.primary_sweep_label.setVisible(False)

            self.polarization_combobox.setVisible(True)
            self.polarization_label.setVisible(True)
            self.plot_type_combobox.setVisible(True)
            self.plot_type_label.setVisible(True)
            self.function_combobox.setVisible(True)
            self.function_label.setVisible(True)

            self.window_combobox.setVisible(True)
            self.window_label.setVisible(True)
            self.upsample_textbox.setVisible(True)
            self.upsample_label.setVisible(True)

            self.upsample_az_textbox.setVisible(False)
            self.upsample_az_label.setVisible(False)
            self.upsample_el_textbox.setVisible(False)
            self.upsample_el_label.setVisible(False)
            self.plane_cut_combobox.setVisible(False)
            self.plane_cut_label.setVisible(False)
            self.plane_offset_textbox.setVisible(False)
            self.plane_offset_label.setVisible(False)

            self.interpolation_combobox.setVisible(False)
            self.interpolation_label.setVisible(False)
            self.extrapolate.setVisible(False)
            self.extrapolate_label.setVisible(False)
            self.gridsize_combobox.setVisible(False)
            self.gridsize_label.setVisible(False)

            self.plot_type_combobox.clear()
            if category == "Range Profile":
                self.plot_type_combobox.addItems(
                    ["Line", "Ribbon", "Plane H", "Plane V", "Projection", "Rotated", "Extruded"]
                )
            else:
                self.plot_type_combobox.addItems(["Donut"])

        elif category == "2D ISAR":
            self.line1.setVisible(True)
            self.line5.setVisible(True)
            self.line6.setVisible(True)
            if self.aspect_range_combobox.currentText() == "Horizontal":
                self.theta_label.setVisible(True)
                self.theta_combobox.setVisible(True)
                self.theta_combobox.setCurrentIndex(self.theta_combobox.count() // 2)
                self.phi_combobox.setVisible(False)
                self.phi_label.setVisible(False)
                self.upsample_az_textbox.setVisible(True)
                self.upsample_az_label.setVisible(True)
                self.upsample_el_textbox.setVisible(False)
                self.upsample_el_label.setVisible(False)
            elif self.aspect_range_combobox.currentText() == "Vertical":
                self.theta_label.setVisible(False)
                self.theta_combobox.setVisible(False)
                self.phi_combobox.setVisible(True)
                self.phi_label.setVisible(True)
                self.phi_combobox.setCurrentIndex(self.phi_combobox.count() // 2)
                self.upsample_az_textbox.setVisible(False)
                self.upsample_az_label.setVisible(False)
                self.upsample_el_textbox.setVisible(True)
                self.upsample_el_label.setVisible(True)
            self.aspect_range_label.setVisible(True)
            self.aspect_range_combobox.setVisible(True)
            self.freq_combobox.setVisible(False)
            self.freq_label.setVisible(False)
            self.primary_sweep_combobox.setVisible(False)
            self.primary_sweep_label.setVisible(False)

            self.polarization_combobox.setVisible(True)
            self.polarization_label.setVisible(True)
            self.plot_type_combobox.setVisible(True)
            self.plot_type_label.setVisible(True)
            self.function_combobox.setVisible(True)
            self.function_label.setVisible(True)

            self.window_combobox.setVisible(True)
            self.window_label.setVisible(True)
            self.upsample_textbox.setVisible(True)
            self.upsample_label.setVisible(True)

            self.plane_cut_combobox.setVisible(False)
            self.plane_cut_label.setVisible(False)
            self.plane_offset_textbox.setVisible(False)
            self.plane_offset_label.setVisible(False)

            self.interpolation_combobox.setVisible(True)
            self.interpolation_label.setVisible(True)
            self.extrapolate.setVisible(True)
            self.extrapolate_label.setVisible(True)
            self.gridsize_combobox.setVisible(True)
            self.gridsize_label.setVisible(True)

            self.plot_type_combobox.clear()
            self.plot_type_combobox.addItems(["Plane", "Relief", "Projection"])

        elif category == "3D ISAR":
            self.theta_combobox.setVisible(False)
            self.theta_label.setVisible(False)
            self.phi_combobox.setVisible(False)
            self.phi_label.setVisible(False)
            self.freq_combobox.setVisible(False)
            self.freq_label.setVisible(False)
            self.aspect_range_combobox.setVisible(False)
            self.aspect_range_label.setVisible(False)
            self.primary_sweep_combobox.setVisible(False)
            self.primary_sweep_label.setVisible(False)
            self.line1.setVisible(False)
            self.line5.setVisible(True)
            self.line6.setVisible(True)
            self.polarization_combobox.setVisible(True)
            self.polarization_label.setVisible(True)
            self.plot_type_combobox.setVisible(True)
            self.plot_type_label.setVisible(True)
            self.function_combobox.setVisible(True)
            self.function_label.setVisible(True)

            self.window_combobox.setVisible(True)
            self.window_label.setVisible(True)
            self.upsample_textbox.setVisible(True)
            self.upsample_label.setVisible(True)

            self.upsample_az_textbox.setVisible(True)
            self.upsample_az_label.setVisible(True)
            self.upsample_el_textbox.setVisible(True)
            self.upsample_el_label.setVisible(True)
            self.plane_cut_combobox.setVisible(False)
            self.plane_cut_label.setVisible(False)
            self.plane_offset_textbox.setVisible(False)
            self.plane_offset_label.setVisible(False)

            self.interpolation_combobox.setVisible(True)
            self.interpolation_label.setVisible(True)
            self.extrapolate.setVisible(True)
            self.extrapolate_label.setVisible(True)
            self.gridsize_combobox.setVisible(True)
            self.gridsize_label.setVisible(True)

            self.plot_type_combobox.clear()
            # TODO: add point-cloud back when it is fast...
            self.plot_type_combobox.addItems(["Iso-surface", "Point cloud", "Projection", "Plane cut"])
        else:
            raise ValueError(f"Unknown category: {category}")

    def update_polarization(self):
        solution = self.solution_combobox.currentText()
        polarization = self.polarization_combobox.currentText()

        if not solution or not polarization:
            self.ui.update_logger("Polarization not found")
            return

        data = properties.radar_explorer.all_scene_actors["plotter"][solution][polarization]

        # Update theta
        self.theta_combobox.blockSignals(True)
        self.theta_combobox.clear()
        thetas = data.rcs_data.available_incident_wave_theta
        self.theta_combobox.addItems(map(str, thetas))
        self.theta_combobox.blockSignals(False)

        # Update phi
        self.phi_combobox.blockSignals(True)
        self.phi_combobox.clear()
        phis = data.rcs_data.available_incident_wave_phi
        self.phi_combobox.addItems(map(str, phis))
        self.phi_combobox.blockSignals(False)

        # Update freq
        self.freq_combobox.blockSignals(True)
        self.freq_combobox.clear()
        freqs = data.rcs_data.frequencies
        self.freq_combobox.addItems(map(str, freqs))
        self.freq_combobox.blockSignals(False)

    def update_plot_type(self):
        plot_type = self.plot_type_combobox.currentText()
        if plot_type == "Plane cut":
            self.plane_cut_combobox.setVisible(True)
            self.plane_cut_label.setVisible(True)
            self.plane_offset_textbox.setVisible(True)
            self.plane_offset_label.setVisible(True)
        else:
            self.plane_cut_combobox.setVisible(False)
            self.plane_cut_label.setVisible(False)
            self.plane_offset_textbox.setVisible(False)
            self.plane_offset_label.setVisible(False)

    def post_3d_button_clicked(self):
        if self.plot_thread is not None:
            self.ui.update_logger("Previous plot is still processing")
            return
        # Compute radar data in a separate thread
        self.plot_thread = Plot3DThread(app=self)
        self.plot_thread.finished_signal.connect(self.plot_finished)
        msg = "Computing data"
        self.ui.update_logger(msg)
        self.ui.update_progress(50)
        self.plot_thread.start()

    def plot_finished(self):
        category = self.main_window.post_3d_menu.category_combobox.currentText()
        self.plotter.plot_model_scene()
        self.ui.update_logger(f"Plot {category}")
        self.plot_thread = None
        self.ui.update_progress(100)

    def post_3d_settings_setup(self):
        layout_row_obj = QHBoxLayout()
        self.post_3d_column_vertical_layout.addLayout(layout_row_obj)

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
