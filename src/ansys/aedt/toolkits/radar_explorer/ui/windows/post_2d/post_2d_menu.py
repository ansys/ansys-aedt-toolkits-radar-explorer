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

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from scipy.interpolate import RegularGridInterpolator

from ansys.aedt.core.generic.constants import CSS4_COLORS
from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter
from ansys.aedt.toolkits.common.ui.utils.widgets import PyIconButton
from ansys.aedt.toolkits.common.ui.utils.widgets import PyTab
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter
from ansys.aedt.toolkits.radar_explorer.ui.models import properties
from ansys.aedt.toolkits.radar_explorer.ui.windows.post_2d.post_2d_column import Ui_LeftColumn
from ansys.aedt.toolkits.radar_explorer.ui.windows.post_2d.post_2d_page import Ui_Plot_Design


class Post2DMenu(object):
    def __init__(self, main_window):
        # General properties
        self.main_window = main_window
        self.ui = main_window.ui
        self.temp_folder = tempfile.mkdtemp()

        self.app_color = self.main_window.ui.themes["app_color"]
        self.title_size = properties.font["title_size"]
        self.active_color = self.app_color["text_active"]
        self.background_color = self.app_color["dark_three"]
        self.background_color_title = self.app_color["dark_four"]
        self.combo_size = self.main_window.properties.font["combo_size"]

        # Add page
        post_2d_menu_index = self.ui.add_page(Ui_Plot_Design)
        self.ui.load_pages.pages.setCurrentIndex(post_2d_menu_index)
        self.post_2d_menu_widget = self.ui.load_pages.pages.currentWidget()

        # Add left column
        new_column_widget = QWidget()
        new_ui = Ui_LeftColumn()
        new_ui.setupUi(new_column_widget)
        self.ui.left_column.menus.menus.addWidget(new_column_widget)
        self.post_2d_column_widget = new_column_widget
        self.post_2d_column_vertical_layout = new_ui.plot_design_vertical_layout

        # Specific properties
        self.post_2d_layout = self.post_2d_menu_widget.findChild(QVBoxLayout, "plot_design_layout")

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

        # Aspect range
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

        # Button
        self.post_2d_button_layout = None
        self.post_2d_button = None
        self.result_combobox = None
        self.result_combo_widget = None
        self.result_label = None
        self.result_2d_tabs = {}
        self.result_widget = {}

        # Settings
        self.line4 = None
        self.post_2d_settings_label = None
        self.post_2d_setting_icon = None
        self.post_2d_settings_column_label = None

        self.post_2d_loaded_tree = None

        self.post_2d_settings_button_layout = None
        self.post_2d_settings_button = None

        # Menu
        self.tab_obj = None
        self.tab_add_new = None

    def setup(self):
        # Solution combobox
        row_returns = self.ui.add_combobox(
            self.post_2d_column_vertical_layout,
            height=40,
            width=[135, 180],
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
            self.post_2d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Category",
            combobox_list=["RCS", "Range Profile", "Waterfall", "2D ISAR", "3D ISAR"],
            font_size=self.combo_size,
        )

        self.category_combo_widget = row_returns[0]
        self.category_label = row_returns[1]
        self.category_combobox = row_returns[2]
        self.category_combobox.currentIndexChanged.connect(lambda: self.update_column())

        self.line1 = self.ui.add_vertical_line(
            self.post_2d_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        # Primary sweep
        row_returns = self.ui.add_combobox(
            self.post_2d_column_vertical_layout,
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
            self.post_2d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Aspect Range",
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
            self.post_2d_column_vertical_layout,
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
            self.post_2d_column_vertical_layout,
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
            self.post_2d_column_vertical_layout,
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
            self.post_2d_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        # Receive polarization
        row_returns = self.ui.add_combobox(
            self.post_2d_column_vertical_layout,
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
            self.post_2d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Plot Type",
            combobox_list=["Line", "Polar"],
            font_size=self.combo_size,
        )

        self.plot_type_combo_widget = row_returns[0]
        self.plot_type_label = row_returns[1]
        self.plot_type_combobox = row_returns[2]

        # Function
        row_returns = self.ui.add_combobox(
            self.post_2d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Function",
            combobox_list=["dB", "abs", "real", "imag", "phase"],
            font_size=self.combo_size,
        )

        self.function_combo_widget = row_returns[0]
        self.function_label = row_returns[1]
        self.function_combobox = row_returns[2]

        # Gridsize
        row_returns = self.ui.add_combobox(
            self.post_2d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Grid Size",
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
            self.post_2d_column_vertical_layout,
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
            self.post_2d_column_vertical_layout,
            height=30,
            width=[135, 180, 0],
            label=["Extrapolate", " "],
            font_size=self.combo_size,
            bg_color=self.app_color["label_off"],
            active_color=self.app_color["label_on"],
            text_color_on=self.app_color["text_foreground"],
            text_color_off=self.app_color["text_foreground"],
            show_on_off=True,
        )
        self.extrapolate_label = row_returns[1]
        self.extrapolate = row_returns[2]
        self.extrapolate.setChecked(True)

        # Window
        row_returns = self.ui.add_combobox(
            self.post_2d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Window",
            combobox_list=["Flat", "Hann", "Hamming"],
            font_size=self.combo_size,
        )

        self.window_combo_widget = row_returns[0]
        self.window_label = row_returns[1]
        self.window_combobox = row_returns[2]

        # Upsample
        row_returns = self.ui.add_textbox(
            self.post_2d_column_vertical_layout,
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
            self.post_2d_column_vertical_layout,
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
            self.post_2d_column_vertical_layout,
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
            self.post_2d_column_vertical_layout,
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
        row_returns = self.ui.add_textbox(
            self.post_2d_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Plane Offset",
            initial_text="0.0",
            font_size=self.combo_size,
        )

        self.plane_offset_text_widget = row_returns[0]
        self.plane_offset_label = row_returns[1]
        self.plane_offset_textbox = row_returns[2]

        self.line3 = self.ui.add_vertical_line(
            self.post_2d_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        # New report combobox
        row_returns = self.ui.add_combobox(
            self.post_2d_column_vertical_layout,
            height=40,
            width=[75, 180],
            label="Target",
            combobox_list=["New Report"],
            font_size=self.combo_size,
        )

        self.result_combo_widget = row_returns[0]
        self.result_label = row_returns[1]
        self.result_combobox = row_returns[2]

        spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.post_2d_column_vertical_layout.addItem(spacer)

        # Plot design
        row_returns = self.ui.add_n_buttons(
            self.post_2d_column_vertical_layout,
            num_buttons=1,
            height=40,
            width=[200],
            text=["Plot"],
            font_size=self.main_window.properties.font["title_size"],
        )

        self.post_2d_button_layout = row_returns[0]
        self.post_2d_button = row_returns[1]
        self.post_2d_button_layout.addWidget(self.post_2d_button)
        self.post_2d_button.clicked.connect(self.post_2d_button_clicked)

        self.line4 = self.ui.add_vertical_line(
            self.post_2d_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        self.post_2d_settings_setup()

        # Menu
        self.tab_obj = PyTab(
            color=self.app_color["combo_color"],
            text_color=self.app_color["text_foreground"],
            selected_color=self.app_color["combo_color"],
            unselected_color=self.app_color["combo_hover"],
        )

        self.tab_add_new = QWidget()
        self.tab_obj.addTab(self.tab_add_new, " + ")
        self.post_2d_layout.addWidget(self.tab_obj)

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
        self.primary_sweep_combobox.blockSignals(True)
        self.primary_sweep_combobox.clear()
        self.primary_sweep_combobox.addItems(["Frequency"])
        if self.theta_combobox.count() > 1:
            self.primary_sweep_combobox.addItems(["Theta"])
        if self.phi_combobox.count() > 1:
            self.primary_sweep_combobox.addItems(["Phi"])
        self.primary_sweep_combobox.blockSignals(False)

    def update_column(self):
        # Populate solutions if new one is added
        if self.solution_combobox.currentText() == "No solution" or self.solution_combobox.count() != len(
            properties.radar_explorer.solution_names
        ):
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
            self.aspect_range_combobox.setVisible(False)
            self.aspect_range_label.setVisible(False)

            self.primary_sweep_combobox.setVisible(True)
            self.primary_sweep_label.setVisible(True)

            primary_sweep = self.primary_sweep_combobox.currentText()
            if primary_sweep == "Frequency":
                self.theta_combobox.setVisible(True)
                self.theta_label.setVisible(True)
                self.phi_combobox.setVisible(True)
                self.phi_label.setVisible(True)
                self.freq_combobox.setVisible(False)
                self.freq_label.setVisible(False)
            elif primary_sweep == "Theta":
                self.theta_combobox.setVisible(False)
                self.theta_label.setVisible(False)
                self.phi_combobox.setVisible(True)
                self.phi_label.setVisible(True)
                self.freq_combobox.setVisible(True)
                self.freq_label.setVisible(True)
            elif primary_sweep == "Phi":
                self.theta_combobox.setVisible(True)
                self.theta_label.setVisible(True)
                self.phi_combobox.setVisible(False)
                self.phi_label.setVisible(False)
                self.freq_combobox.setVisible(True)
                self.freq_label.setVisible(True)

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
            self.plot_type_combobox.addItems(["Line", "Polar"])

        elif category == "Range Profile" or category == "Waterfall":
            self.line1.setVisible(True)
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
                self.plot_type_combobox.addItems(["Line"])
            else:
                self.plot_type_combobox.addItems(["Rectangular", "Polar"])

        elif category == "2D ISAR":
            self.line1.setVisible(True)  # revisit if the data comes from 3D ISAR
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
            self.plot_type_combobox.setVisible(False)  # revisit if the data comes from 3D ISAR
            self.plot_type_label.setVisible(False)  # revisit if the data comes from 3D ISAR
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
            self.plot_type_combobox.addItems(["Plane"])

        else:
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
            self.plane_cut_combobox.setVisible(True)
            self.plane_cut_label.setVisible(True)
            self.plane_offset_textbox.setVisible(True)
            self.plane_offset_label.setVisible(True)

            self.interpolation_combobox.setVisible(True)
            self.interpolation_label.setVisible(True)
            self.extrapolate.setVisible(True)
            self.extrapolate_label.setVisible(True)
            self.gridsize_combobox.setVisible(True)
            self.gridsize_label.setVisible(True)

            self.plot_type_combobox.clear()
            self.plot_type_combobox.addItems(["Plane Cut"])

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

    def post_2d_button_clicked(self):
        solution = self.solution_combobox.currentText()

        category = self.category_combobox.currentText()
        primary_sweep = self.primary_sweep_combobox.currentText()
        theta = self.theta_combobox.currentText()
        phi = self.phi_combobox.currentText()
        freq = self.freq_combobox.currentText()

        plot_type = self.plot_type_combobox.currentText()
        polarization = self.polarization_combobox.currentText()
        window = self.window_combobox.currentText()
        upsample = self.upsample_textbox.text()
        upsample_az = self.upsample_az_textbox.text()
        upsample_el = self.upsample_el_textbox.text()
        function_expression = self.function_combobox.currentText()
        interpolation = self.interpolation_combobox.currentText()
        extrapolate = self.extrapolate.isChecked()
        gridsize = self.gridsize_combobox.currentText()

        data: MonostaticRCSPlotter = None
        if solution != "No solution":
            data = properties.radar_explorer.all_scene_actors["plotter"][solution][polarization]

        tab_selected = self.tab_obj.tabText(self.tab_obj.tabBar().currentIndex())

        if tab_selected in self.result_2d_tabs.keys():
            plot_layout_comp = self.result_2d_tabs[tab_selected]
        else:
            return False

        selected_report = self.result_combobox.currentText()

        # Matplotlib canvas
        if "dark" in self.ui.themes["theme_name"]:
            plt.style.use("dark_background")
        else:
            plt.style.use("classic")

        if selected_report == "New Report":
            canvas = FigureCanvas()
            figure_toolbar = NavigationToolbar(canvas)
            toolbar_background_color = self.ui.themes["app_color"]["bg_three"]
            figure_toolbar.setStyleSheet(f"background-color: {toolbar_background_color};")

            layout = QVBoxLayout()
            layout.addWidget(figure_toolbar)
            layout.addWidget(canvas)
            toolbar_and_fig = QWidget()
            toolbar_and_fig.setLayout(layout)
            plot_layout_comp.addWidget(toolbar_and_fig)

            increment = 1
            items = [self.result_combobox.itemText(i) for i in range(self.result_combobox.count())]
            selected_report = f"Report_{increment}"
            while selected_report in items:
                selected_report = f"Report_{increment}"
                increment += 1

            if selected_report not in properties.radar_explorer.all_scene_actors["results"]:
                properties.radar_explorer.all_scene_actors["results"][selected_report] = {}

            # Save Canvas for future usage
            if not properties.radar_explorer.reports[tab_selected]:
                properties.radar_explorer.reports[tab_selected] = {}
            properties.radar_explorer.reports[tab_selected][selected_report] = toolbar_and_fig

            self.result_combobox.addItems([selected_report])

        is_polar = False
        if plot_type == "Polar":
            is_polar = True

        # Get selected Canvas
        existing_widget = properties.radar_explorer.reports[tab_selected][selected_report]
        canvas = existing_widget.layout().itemAt(1).widget()
        toolbar = existing_widget.layout().itemAt(0).widget()
        canvas.figure.clf()

        if data:
            data.rcs_data.interpolation = interpolation
            data.rcs_data.extrapolate = extrapolate
            data.rcs_data.gridsize = gridsize
            if function_expression == "dB":
                function_expression = "dB20"
            if function_expression == "phase":
                function_expression = "ang_deg"
            data.rcs_data.data_conversion_function = function_expression
            if category == "RCS":
                if primary_sweep == "Theta":
                    primary_sweep = "IWaveTheta"
                    secondary_sweep = "IWavePhi"
                    secondary_sweep_value = float(phi)
                    data.rcs_data.frequency = float(freq)
                    name = f"{polarization}, {secondary_sweep}={secondary_sweep_value}, Freq={freq}"
                elif primary_sweep == "Frequency":
                    primary_sweep = "Freq"
                    secondary_sweep = "IWaveTheta"
                    secondary_sweep_value = float(theta)
                    data.rcs_data.incident_wave_phi = float(phi)
                    name = f"{polarization}, {secondary_sweep}={secondary_sweep_value}, IWavePhi={phi}"

                else:
                    primary_sweep = "IWavePhi"
                    secondary_sweep = "IWaveTheta"
                    secondary_sweep_value = float(theta)
                    data.rcs_data.frequency = float(freq)
                    name = f"{polarization}, {secondary_sweep}={secondary_sweep_value}, Freq={freq}"

                report_plotter = data.plot_rcs(
                    show=False,
                    primary_sweep=primary_sweep,
                    secondary_sweep=secondary_sweep,
                    secondary_sweep_value=secondary_sweep_value,
                    title="Monostatic RCS",
                    is_polar=is_polar,
                )

                properties.radar_explorer.all_scene_actors["results"][selected_report][name] = report_plotter

            elif category == "Range Profile":
                primary_sweep = "IWaveTheta"
                secondary_sweep = "IWavePhi"
                primary_sweep_value = float(theta)
                secondary_sweep_value = float(phi)
                data.rcs_data.incident_wave_phi = float(phi)
                data.rcs_data.incident_wave_theta = float(theta)
                data.rcs_data.window = window
                data.rcs_data.window_size = int(upsample)
                name = (
                    f"{polarization}, {primary_sweep}={primary_sweep_value}, {secondary_sweep}={secondary_sweep_value}"
                )

                report_plotter = data.plot_range_profile(show=False, title="Range Profile")

                properties.radar_explorer.all_scene_actors["results"][selected_report][name] = report_plotter

            elif category == "Waterfall":
                data.rcs_data.aspect_range = self.aspect_range_combobox.currentText()
                primary_sweep = "IWaveTheta"
                secondary_sweep = "IWavePhi"
                primary_sweep_value = float(theta)
                secondary_sweep_value = float(phi)
                data.rcs_data.incident_wave_phi = float(phi)
                data.rcs_data.incident_wave_theta = float(theta)
                data.rcs_data.window = window
                data.rcs_data.window_size = int(upsample)
                name = (
                    f"{polarization}, {primary_sweep}={primary_sweep_value}, {secondary_sweep}={secondary_sweep_value}"
                )

                report_plotter = data.plot_waterfall(show=False, is_polar=is_polar, figure=canvas.figure, title=None)

                properties.radar_explorer.all_scene_actors["results"][selected_report][name] = report_plotter

            elif category == "2D ISAR":
                data.rcs_data.aspect_range = self.aspect_range_combobox.currentText()
                data.rcs_data.window = window
                data.rcs_data.upsample_range = int(upsample)
                data.rcs_data.incident_wave_phi = float(phi)
                data.rcs_data.incident_wave_theta = float(theta)
                data.rcs_data.upsample_azimuth = int(upsample_az)
                data.rcs_data.upsample_elevation = int(upsample_el)
                name = f"{polarization}, {function_expression}"

                report_plotter = data.plot_isar_2d(show=False, figure=canvas.figure, title=None)

                properties.radar_explorer.all_scene_actors["results"][selected_report][name] = report_plotter

            else:
                data.rcs_data.aspect_range = None
                data.rcs_data.window = window
                data.rcs_data.upsample_range = int(upsample)
                data.rcs_data.upsample_azimuth = int(upsample_az)
                data.rcs_data.upsample_elevation = int(upsample_el)
                name = f"{polarization}, {function_expression}"
                plane_cut = self.plane_cut_combobox.currentText()
                plane_offset = self.plane_offset_textbox.text()

                report_plotter = data.plot_isar_3d(
                    show=False,
                    figure=canvas.figure,
                    title=None,
                    plane_cut=plane_cut,
                    plane_offset=float(plane_offset),
                )

                properties.radar_explorer.all_scene_actors["results"][selected_report][name] = report_plotter

        if "dark" in self.ui.themes["theme_name"]:
            plt.style.use("dark_background")
        else:
            plt.style.use("classic")

        # Get traces
        k = 0
        if data:
            # Plot traces in Canvas
            if category in ["RCS", "Range Profile"]:
                new_plotter = ReportPlotter()
                for report_name, report in properties.radar_explorer.all_scene_actors["results"][
                    selected_report
                ].items():
                    name = report.trace_names[0]
                    trace = report.traces[name]
                    props = {
                        "x_label": trace.x_label,
                        "y_label": trace.y_label,
                        "line_color": list(CSS4_COLORS.keys())[k],
                    }
                    k += 1
                    if k == len(list(CSS4_COLORS.keys())):
                        k = 0
                    new_plotter.add_trace([trace.cartesian_data[0], trace.cartesian_data[1]], 0, props, report_name)
                if not is_polar:
                    _ = new_plotter.plot_2d(show=False, figure=canvas.figure)
                else:
                    _ = new_plotter.plot_polar(show=False, figure=canvas.figure)

        else:
            ax = canvas.figure.add_subplot(111)

            message = "Ansys"
            x_data = range(len(message))
            y_level = np.random.randint(1, 6)

            # Plot each letter as a text point on the same Y level
            for x, letter in zip(x_data, message):
                ax.text(x, y_level, letter, fontsize=20, ha="center", va="center", color=self.app_color["icon_color"])

            # Set limits and labels for clarity
            ax.set_xlim(-1, len(message))
            ax.set_ylim(0, 6)
            ax.set_xlabel("X-Axis (Letters)")
            ax.set_ylabel("Y-Axis (Fixed Level)")

        properties.radar_explorer.reports[tab_selected][selected_report].layout().update()
        properties.radar_explorer.reports[tab_selected][selected_report].adjustSize()
        toolbar.update()
        canvas.flush_events()
        canvas.draw()

    def add_tab(self, name="Results"):
        # function that incrments a name if it already exists in a list of names
        def increment_name(name, all_tab_names):
            if name in all_tab_names:
                # split the name into a list of words
                name_list = name.split(" ")
                # check if the last word is a number
                if name_list[-1].isdigit():
                    # if it is, increment it
                    name_list[-1] = str(int(name_list[-1]) + 1)
                else:
                    # if it isn't, add a 2 to the end
                    name_list.append("2")
                # join the list back into a string
                name = " ".join(name_list)
                # check if the new name is in the list of all tab names
                if name in all_tab_names:
                    # if it is, call this function again
                    name = increment_name(name, all_tab_names)
            return name

        # create new tab as long the "+" tab is selected
        self.tab_obj.blockSignals(True)
        num_tabs = self.tab_obj.tabBar().count()
        selected_tab = self.tab_obj.tabText(self.tab_obj.tabBar().currentIndex())
        if selected_tab == " + ":  # this is the create new tab button
            self.result_combobox.setCurrentText("New Report")
            all_tab_names = [
                self.tab_obj.tabText(i) for i in range(num_tabs)
            ]  # gen names of all tabs within self.tab_obj
            new_tab = QWidget()
            tab_layout = QHBoxLayout(new_tab)
            hlayout = QHBoxLayout()
            tab_layout.addLayout(hlayout)
            name = increment_name(name, all_tab_names)
            self.tab_obj.addTab(new_tab, name)
            num_tabs = self.tab_obj.tabBar().count()
            self.tab_obj.tabBar().moveTab(num_tabs - 2, num_tabs - 1)  # move the add new tab to the end
            self.tab_obj.tabBar().setCurrentIndex(num_tabs - 2)
            self.result_2d_tabs[name] = tab_layout

            # Property to save canvas
            properties.radar_explorer.reports[name] = None
        self.tab_obj.blockSignals(False)

    def remove_tab(self, name):
        self.tab_obj.blockSignals(True)
        num_tabs = self.tab_obj.tabBar().count()
        tab_index = None
        for i in range(num_tabs):
            if self.tab_obj.tabText(i) == name:
                tab_index = i
                break

        if tab_index is not None and name != " + " and name != "Results":
            self.tab_obj.removeTab(tab_index)

            if name in self.result_2d_tabs:
                del self.result_2d_tabs[name]
            if name in properties.radar_explorer.reports:
                available_reports = list(properties.radar_explorer.reports[name].keys())
                del properties.radar_explorer.reports[name]
                for report in available_reports:
                    if report in properties.radar_explorer.all_scene_actors["results"]:
                        del properties.radar_explorer.all_scene_actors["results"][report]
        self.tab_obj.blockSignals(False)

    def post_2d_settings_setup(self):
        layout_row_obj = QHBoxLayout()
        self.post_2d_column_vertical_layout.addLayout(layout_row_obj)

        self.post_2d_settings_label = QLabel("Settings")
        self.post_2d_settings_label.setStyleSheet(
            f"font-size: {self.title_size}pt; color: {self.active_color};font-weight: bold;"
        )
        layout_row_obj.addWidget(self.post_2d_settings_label)

        theme = self.main_window.ui.themes
        self.post_2d_setting_icon = PyIconButton(
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
        self.post_2d_setting_icon.setMinimumHeight(40)
        layout_row_obj.addWidget(self.post_2d_setting_icon)
        self.post_2d_setting_icon.clicked.connect(lambda: self.post_2d_settings())

    def post_2d_settings(self):
        self.main_window.settings_menu.hide_widgets()

        if not self.post_2d_loaded_tree:
            # Column
            layout = QVBoxLayout()

            # Post 3D Model title
            self.post_2d_settings_column_label = QLabel("Plot settings")
            self.post_2d_settings_column_label.setStyleSheet(
                f"font-size: {self.combo_size}pt; color: {self.active_color};font-weight: bold;"
            )
            layout.addWidget(self.post_2d_settings_column_label)

            # Spacer
            spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Minimum)
            layout.addItem(spacer)

            self.post_2d_loaded_tree = QTreeWidget()
            self.post_2d_loaded_tree.setHeaderLabels(["Result", "Report", "Delete"])
            self.post_2d_loaded_tree.setObjectName("post_2d_loaded_tree")

            table_style = (
                "QTreeWidget {{ background: {_bg_color}; color: {_active_color}; font-size: {"
                "_font_size}pt;}}"
                "QTreeWidget:item:selected {{background:  {_selection};}}"
                "QTreeWidget:item:hover {{background: {_hover};}}"
            )

            custom_style = table_style.format(
                _bg_color=self.app_color["combo_color"],
                _font_size=self.combo_size,
                _active_color=self.active_color,
                _hover=self.app_color["combo_hover"],
                _selection=self.background_color,
            )

            self.post_2d_loaded_tree.setStyleSheet(custom_style)

            header = self.post_2d_loaded_tree.header()
            header.setStyleSheet(f"""
                                        QHeaderView::section {{
                                            background-color: {self.background_color};
                                            color: {self.active_color};
                                            font-size: {self.combo_size}pt;
                                            padding: 2px;
                                        }}
                                    """)
            self.post_2d_loaded_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            layout.addWidget(self.post_2d_loaded_tree)

            # Plot design
            row_returns = self.ui.add_n_buttons(
                layout,
                num_buttons=1,
                height=40,
                width=[180],
                text=["Apply"],
                font_size=self.main_window.properties.font["title_size"],
            )

            self.post_2d_settings_button_layout = row_returns[0]
            self.post_2d_settings_button = row_returns[1]
            self.post_2d_settings_button_layout.addWidget(self.post_2d_settings_button)
            self.post_2d_settings_button.clicked.connect(self.post_2d_settings_clicked)

            self.main_window.ui.right_column.menus.settings_vertical_layout.addLayout(layout)
        else:
            self.post_2d_loaded_tree.setVisible(True)
            self.post_2d_settings_button.setVisible(True)

        self.main_window.home_menu.right_column_visibility(False)

        self.populate_post_2d_tree()

        self.ui.set_right_column_menu("Post 2D settings")
        self.ui.toggle_right_column()

    def populate_post_2d_tree(self):
        # Populate tree
        self.post_2d_loaded_tree.blockSignals(True)
        self.post_2d_loaded_tree.clear()

        for report_name, report in properties.radar_explorer.reports.items():
            main_item = QTreeWidgetItem(self.post_2d_loaded_tree, [report_name, "", ""])

            main_item.setFlags(main_item.flags() | Qt.ItemIsUserCheckable)
            main_item.setCheckState(2, Qt.Unchecked)

            if report:
                for result_name, result in report.items():
                    item = QTreeWidgetItem(main_item, ["", result_name, ""])
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(2, Qt.Unchecked)
            self.post_2d_loaded_tree.addTopLevelItem(main_item)

        self.post_2d_loaded_tree.expandAll()
        self.post_2d_loaded_tree.blockSignals(False)

    def right_column_visibility(self, visible=False):
        if self.post_2d_loaded_tree:
            self.post_2d_loaded_tree.setVisible(visible)
            self.post_2d_settings_button.setVisible(visible)
            self.post_2d_settings_column_label.setVisible(visible)

    def post_2d_settings_clicked(self):
        self.post_2d_loaded_tree.blockSignals(True)
        for i in range(self.post_2d_loaded_tree.topLevelItemCount()):
            main_item = self.post_2d_loaded_tree.topLevelItem(i)
            main_state = main_item.checkState(2) == Qt.Checked
            result_name = main_item.text(0)
            if main_state:
                self.remove_tab(result_name)

            else:
                for j in range(main_item.childCount()):
                    child_item = main_item.child(j)
                    child_state = child_item.checkState(2) == Qt.Checked
                    if child_state:
                        child_name = child_item.text(1)
                        properties.radar_explorer.reports[result_name][child_name].deleteLater()
                        del properties.radar_explorer.reports[result_name][child_name]
                        del properties.radar_explorer.all_scene_actors["results"][child_name]

        # Update report
        self.result_combobox.clear()
        self.result_combobox.addItems(["New Report"])
        self.result_combobox.addItems(list(properties.radar_explorer.all_scene_actors["results"].keys()))

        # Update table
        self.post_2d_settings()

        self.post_2d_loaded_tree.blockSignals(True)
