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

import numpy as np
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.toolkits.common.ui.utils.widgets import PyIconButton
from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.domain_transforms import DomainTransforms
from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.utils import split_num_units
from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.utils import unit_converter_rcs
from ansys.aedt.toolkits.radar_explorer.ui.models import properties
from ansys.aedt.toolkits.radar_explorer.ui.utils.widgets.py_line_edit_precision_unit.py_line_edit_with_float import (
    PyLineEditWithFloat,
)
from ansys.aedt.toolkits.radar_explorer.ui.windows.common_windows_utils import CommonWindowUtilsRCS
from ansys.aedt.toolkits.radar_explorer.ui.windows.mode.mode_column import Ui_LeftColumn
from ansys.aedt.toolkits.radar_explorer.ui.windows.mode.mode_page import Ui_Plot_Design


SELECT_MODE_LIST = ["Range Profile", "2D ISAR", "3D ISAR"]
"""List of available modes in the mode selection combo box."""

RANGE_MODE_LIST = ["System", "Performance"]
"""List of available range modes in the range mode selection combo box."""


class ModeSelectMenu(object):
    def __init__(self, main_window):
        # General properties
        self.class_name = "ModeMenu"
        self.main_window = main_window
        self.ui = main_window.ui

        self.dark_mode = True if "dark" in self.main_window.ui.themes["theme_name"] else False
        self.app_color = self.main_window.ui.themes["app_color"]
        self.title_size = properties.font["title_size"]
        self.combo_size = properties.font["combo_size"]
        self.active_color = self.app_color["text_active"]
        self.background_color = self.app_color["dark_three"]
        self.background_color_title = self.app_color["dark_four"]

        # Add page
        mode_menu_index = self.ui.add_page(Ui_Plot_Design)
        self.ui.load_pages.pages.setCurrentIndex(mode_menu_index)
        self.mode_menu_widget = self.ui.load_pages.pages.currentWidget()

        # Add left column
        new_column_widget = QWidget()
        new_ui = Ui_LeftColumn()
        new_ui.setupUi(new_column_widget)
        self.ui.left_column.menus.menus.addWidget(new_column_widget)
        self.mode_select_column_widget = new_column_widget
        self.mode_select_column_vertical_layout = new_ui.mode_select_vertical_layout

        # Specific properties
        self.mode_layout = self.mode_menu_widget.findChild(QVBoxLayout, "plot_design_layout")

        self.mode_selection_combo_widget = None
        self.mode_selection_label = None
        self.mode_selection_combobox = None

        self.line1 = None

        self.center_freq_widget = None
        self.center_freq_label = None
        self.center_freq_textbox = None

        self.azimuth_divider = None

        self.range_mode_selection_combo_widget = None
        self.range_mode_selection_label = None
        self.range_mode_selection_combobox = None

        self.fft_bandwidth_widget = None
        self.fft_bandwidth_label = None
        self.fft_bandwidth_textbox = None

        self.num_freq_widget = None
        self.num_freq_label = None
        self.num_freq_textbox = None

        self.max_range_widget = None
        self.max_range_label = None
        self.max_range_textbox = None

        self.range_res_widget = None
        self.range_res_label = None
        self.range_res_textbox = None

        self.range_divider = None
        self.center_freq_divider = None

        self.azimuth_mode_selection_combo_widget = None
        self.azimuth_mode_selection_label = None
        self.azimuth_mode_selection_combobox = None

        self.aspect_angle_phi_widget = None
        self.aspect_angle_phi_label = None
        self.aspect_angle_phi_textbox = None

        self.num_inc_phi_widget = None
        self.num_inc_phi_label = None
        self.num_inc_phi_textbox = None

        self.max_cross_range_az_widget = None
        self.max_cross_range_az_label = None
        self.max_cross_range_az_textbox = None

        self.cross_range_az_res_widget = None
        self.cross_range_az_res_label = None
        self.cross_range_az_res_textbox = None

        self.elevation_mode_selection_combo_widget = None
        self.elevation_mode_selection_label = None
        self.elevation_mode_selection_combobox = None

        self.elevation_divider = None

        self.aspect_angle_theta_widget = None
        self.aspect_angle_theta_label = None
        self.aspect_angle_theta_textbox = None

        self.num_inc_theta_widget = None
        self.num_inc_theta_label = None
        self.num_inc_theta_textbox = None

        self.max_cross_range_el_widget = None
        self.max_cross_range_el_label = None
        self.max_cross_range_el_textbox = None

        self.cross_range_el_res_widget = None
        self.cross_range_el_res_label = None
        self.cross_range_el_res_textbox = None

        self.preview_toggle = None
        self.plotter = self.main_window.home_menu.plotter

        self.sim_freq_lower = None
        self.sim_freq_upper = None

        self.post_3d_settings_label = None
        self.post_3d_setting_icon = None
        self.line1 = None

        # Common RCS Utils
        self.rcs_utils = CommonWindowUtilsRCS(self.main_window.ui.themes)

    def setup(self):
        row_returns = self.ui.add_combobox(
            self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Select Mode",
            combobox_list=SELECT_MODE_LIST,
            font_size=self.combo_size,
        )
        self.mode_selection_combo_widget = row_returns[0]
        self.mode_selection_label = row_returns[1]
        self.mode_selection_combobox = row_returns[2]
        self.mode_selection_combobox.currentTextChanged.connect(self.mode_state_changed)

        self.line1 = self.ui.add_vertical_line(
            self.mode_select_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        center_frequency = Quantity(properties.radar_explorer.center_frequency)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Center Frequency",
            value=center_frequency.value,
            precision=properties.radar_explorer.precision,
            unit=center_frequency.unit,
            font_size=self.combo_size,
        )
        self.center_freq_widget = row_returns[0]
        self.center_freq_label = row_returns[1]
        self.center_freq_textbox = row_returns[2]
        self.center_freq_textbox.editingFinished.connect(self.update_center_freq)

        self.center_freq_divider = self.ui.add_vertical_line(
            self.mode_select_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 0]
        )

        # Range Frequency

        row_returns = self.ui.add_combobox(
            self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Range Specs",
            combobox_list=RANGE_MODE_LIST,
            font_size=self.combo_size,
        )
        self.range_mode_selection_combo_widget = row_returns[0]
        self.range_mode_selection_label = row_returns[1]
        self.range_mode_selection_combobox = row_returns[2]
        self.range_mode_selection_combobox.currentTextChanged.connect(self.mode_state_changed)

        fft_bandwidth = Quantity(properties.radar_explorer.fft_bandwidth)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="FFT Bandwidth",
            value=fft_bandwidth.value,
            unit=fft_bandwidth.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )
        self.fft_bandwidth_widget = row_returns[0]
        self.fft_bandwidth_label = row_returns[1]
        self.fft_bandwidth_textbox = row_returns[2]
        self.fft_bandwidth_textbox.editingFinished.connect(self.update_range_sys2perf)

        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Num. Freq.",
            value=properties.radar_explorer.frequencies,
            unit="",
            val_type=int,
            precision=0,
            font_size=self.combo_size,
        )
        self.num_freq_widget = row_returns[0]
        self.num_freq_label = row_returns[1]
        self.num_freq_textbox = row_returns[2]
        self.num_freq_textbox.editingFinished.connect(self.update_range_sys2perf)

        max_range = Quantity(properties.radar_explorer.maximum_range)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Max Range",
            value=max_range.value,
            unit=max_range.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )
        self.max_range_widget = row_returns[0]
        self.max_range_label = row_returns[1]
        self.max_range_textbox = row_returns[2]
        self.max_range_textbox.editingFinished.connect(self.update_range_perf2sys)

        range_res = Quantity(properties.radar_explorer.range_resolution)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Range Res.",
            value=range_res.value,
            unit=range_res.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )
        self.range_res_widget = row_returns[0]
        self.range_res_label = row_returns[1]
        self.range_res_textbox = row_returns[2]
        self.range_res_textbox.editingFinished.connect(self.update_range_perf2sys)

        self.range_divider = self.ui.add_vertical_line(
            self.mode_select_column_vertical_layout, top_spacer=[0, 0], bot_spacer=[0, 0]
        )

        # Azimuth

        row_returns = self.ui.add_combobox(
            self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Azimuth Specs",
            combobox_list=["System", "Performance"],
            font_size=self.combo_size,
        )
        self.azimuth_mode_selection_combo_widget = row_returns[0]
        self.azimuth_mode_selection_label = row_returns[1]
        self.azimuth_mode_selection_combobox = row_returns[2]
        self.azimuth_mode_selection_combobox.currentTextChanged.connect(self.mode_state_changed)

        azimuth_span = Quantity(properties.radar_explorer.azimuth_span)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Azimuth Span",
            value=azimuth_span.value,
            unit=azimuth_span.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )
        self.aspect_angle_phi_widget = row_returns[0]
        self.aspect_angle_phi_label = row_returns[1]
        self.aspect_angle_phi_textbox = row_returns[2]
        self.aspect_angle_phi_textbox.editingFinished.connect(self.update_crossrange_az_sys2perf)

        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Num. Az. Angles",
            value=properties.radar_explorer.azimuth_angles,
            val_type=int,
            precision=0,
            unit="",
            font_size=self.combo_size,
        )
        self.num_inc_phi_widget = row_returns[0]
        self.num_inc_phi_label = row_returns[1]
        self.num_inc_phi_textbox = row_returns[2]
        self.num_inc_phi_textbox.editingFinished.connect(self.update_crossrange_az_sys2perf)

        maximum_cross_range_azimuth = Quantity(properties.radar_explorer.maximum_cross_range_azimuth)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="CrossRange Az. Period",
            value=maximum_cross_range_azimuth.value,
            unit=maximum_cross_range_azimuth.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )
        self.max_cross_range_az_widget = row_returns[0]
        self.max_cross_range_az_label = row_returns[1]
        self.max_cross_range_az_textbox = row_returns[2]
        self.max_cross_range_az_textbox.editingFinished.connect(self.update_crossrange_az_perf2sys)

        cross_range_azimuth_resolution = Quantity(properties.radar_explorer.cross_range_azimuth_resolution)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="CrossRange Az. Res.",
            value=cross_range_azimuth_resolution.value,
            unit=cross_range_azimuth_resolution.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )
        self.cross_range_az_res_widget = row_returns[0]
        self.cross_range_az_res_label = row_returns[1]
        self.cross_range_az_res_textbox = row_returns[2]
        self.cross_range_az_res_textbox.editingFinished.connect(self.update_crossrange_az_perf2sys)

        self.azimuth_divider = self.ui.add_vertical_line(
            self.mode_select_column_vertical_layout, top_spacer=[0, 0], bot_spacer=[0, 0]
        )

        # Elevation

        row_returns = self.ui.add_combobox(
            self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Elevation Specs",
            combobox_list=["System", "Performance"],
            font_size=self.combo_size,
        )
        self.elevation_mode_selection_combo_widget = row_returns[0]
        self.elevation_mode_selection_label = row_returns[1]
        self.elevation_mode_selection_combobox = row_returns[2]
        self.elevation_mode_selection_combobox.currentTextChanged.connect(self.mode_state_changed)

        elevation_span = Quantity(properties.radar_explorer.elevation_span)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Elevation Span",
            value=elevation_span.value,
            unit=elevation_span.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )
        self.aspect_angle_theta_widget = row_returns[0]
        self.aspect_angle_theta_label = row_returns[1]
        self.aspect_angle_theta_textbox = row_returns[2]
        self.aspect_angle_theta_textbox.editingFinished.connect(self.update_crossrange_el_sys2perf)

        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Num. El. Angles",
            value=properties.radar_explorer.elevation_angles,
            val_type=int,
            precision=0,
            unit="",
            font_size=self.combo_size,
        )
        self.num_inc_theta_widget = row_returns[0]
        self.num_inc_theta_label = row_returns[1]
        self.num_inc_theta_textbox = row_returns[2]
        self.num_inc_theta_textbox.editingFinished.connect(self.update_crossrange_el_sys2perf)

        maximum_cross_range_elevation = Quantity(properties.radar_explorer.maximum_cross_range_elevation)

        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="CrossRange El. Period",
            value=maximum_cross_range_elevation.value,
            unit=maximum_cross_range_elevation.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )
        self.max_cross_range_el_widget = row_returns[0]
        self.max_cross_range_el_label = row_returns[1]
        self.max_cross_range_el_textbox = row_returns[2]
        self.max_cross_range_el_textbox.editingFinished.connect(self.update_crossrange_el_perf2sys)

        maximum_cross_range_elevation = Quantity(properties.radar_explorer.maximum_cross_range_elevation)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.mode_select_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="CrossRange El. Res.",
            value=maximum_cross_range_elevation.value,
            unit=maximum_cross_range_elevation.unit,
            font_size=self.combo_size,
        )
        self.cross_range_el_res_widget = row_returns[0]
        self.cross_range_el_res_label = row_returns[1]
        self.cross_range_el_res_textbox = row_returns[2]
        self.cross_range_el_res_textbox.editingFinished.connect(self.update_crossrange_el_perf2sys)

        self.elevation_divider = self.ui.add_vertical_line(
            self.mode_select_column_vertical_layout, top_spacer=[0, 0], bot_spacer=[0, 10]
        )

        self.__preview_toggle()
        self.preview_toggle.stateChanged.connect(self.toggle_state_changed)

        self.line1 = self.ui.add_vertical_line(
            self.mode_select_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        self.post_3d_settings_setup()

        # calculate range/cross range and update it for first time
        self.update_range_sys2perf()
        self.update_crossrange_az_sys2perf()
        self.update_crossrange_el_sys2perf()

        # Page
        self.initialize_plotter()
        self.on_tab_changed()

        self.mode_state_changed()

    def on_tab_changed(self):
        if self.main_window.ui.get_selected_menu() == "mode_menu":
            self.plotter.reparent_to_placeholder(self.class_name)

    def initialize_plotter(self):
        self.plotter.add_to_window(self.class_name, self.mode_layout)

    def toggle_state_changed(self):
        if self.preview_toggle.isChecked():
            self.show_preview()
        else:
            properties.radar_explorer.all_scene_actors["annotations"]["range_profile"] = None
            properties.radar_explorer.all_scene_actors["annotations"]["isar_2d"] = None
            properties.radar_explorer.all_scene_actors["annotations"]["isar_3d"] = None
            properties.radar_explorer.all_scene_actors["annotations"]["waterfall"] = None
            self.plotter.plot_model_scene()

    def show_preview(self):
        category = self.mode_selection_combobox.currentText()

        max_range = self.max_range_textbox.text()
        resolution = self.range_res_textbox.text()
        max_range, _ = split_num_units(max_range)
        resolution, _ = split_num_units(resolution)

        aspect_ang_phi = self.aspect_angle_phi_textbox.text()
        phi_num = self.num_inc_phi_textbox.text()
        aspect_ang_phi, _ = split_num_units(aspect_ang_phi)
        phi_num, _ = split_num_units(phi_num)
        phi_num = int(phi_num)

        size_az_range = self.max_cross_range_az_textbox.text()
        cross_az_resolution = self.cross_range_az_res_textbox.text()
        size_az_range, _ = split_num_units(size_az_range)
        cross_az_resolution, _ = split_num_units(cross_az_resolution)

        size_el_range = self.max_cross_range_el_textbox.text()
        cross_el_resolution = self.cross_range_el_res_textbox.text()
        size_el_range, _ = split_num_units(size_el_range)
        cross_el_resolution, _ = split_num_units(cross_el_resolution)

        # TODO: Take care of the units. RCS object could be not in meters

        solution_name = self.main_window.incident_wave_menu.solution_selection_combobox.currentText()
        if solution_name == "No solution":
            rcs_object = self.ui.app.load_rcs_data_from_file()
        else:
            rcs_objects = properties.radar_explorer.all_scene_actors["plotter"][solution_name]
            first_key = list(rcs_objects.keys())[0]
            rcs_object = rcs_objects[first_key]

        rcs_object.clear_scene()
        properties.radar_explorer.all_scene_actors["annotations"]["isar_2d"] = None
        properties.radar_explorer.all_scene_actors["annotations"]["isar_3d"] = None
        properties.radar_explorer.all_scene_actors["annotations"]["range_profile"] = None
        properties.radar_explorer.all_scene_actors["annotations"]["waterfall"] = None

        if self.dark_mode:
            tick_color = "#FFFFFF"
        else:
            tick_color = "#000000"

        wrong_input = False
        if category == "Range Profile":
            rcs_object.add_range_profile_settings(
                size_range=max_range, range_resolution=resolution, tick_color=tick_color
            )
            if "range_profile" in rcs_object.all_scene_actors["annotations"].keys():
                properties.radar_explorer.all_scene_actors["annotations"]["range_profile"] = (
                    rcs_object.all_scene_actors
                )["annotations"]["range_profile"]
            else:
                wrong_input = True
        elif category == "2D ISAR":
            rcs_object.add_isar_2d_settings(
                size_range=max_range,
                range_resolution=resolution,
                size_cross_range=size_az_range,
                cross_range_resolution=cross_az_resolution,
                tick_color=tick_color,
            )
            if "isar_2d" in rcs_object.all_scene_actors["annotations"].keys():
                properties.radar_explorer.all_scene_actors["annotations"]["isar_2d"] = (rcs_object.all_scene_actors)[
                    "annotations"
                ]["isar_2d"]
            else:
                wrong_input = True
        elif category == "3D ISAR":
            rcs_object.add_isar_3d_settings(
                size_range=max_range,
                range_resolution=resolution,
                size_cross_range=size_az_range,
                cross_range_resolution=cross_az_resolution,
                size_elevation_range=size_el_range,
                elevation_range_resolution=cross_el_resolution,
                tick_color=tick_color,
            )
            if "isar_3d" in rcs_object.all_scene_actors["annotations"].keys():
                properties.radar_explorer.all_scene_actors["annotations"]["isar_3d"] = (rcs_object.all_scene_actors)[
                    "annotations"
                ]["isar_3d"]
            else:
                wrong_input = True

        if "Ansys_scene" in properties.radar_explorer.all_scene_actors["model"].keys():
            self.main_window.home_menu.reset_scene()

        if not wrong_input:
            self.plotter.plot_model_scene()
        else:
            self.ui.update_logger(f"Wrong input settings for {category}")
        self.ui.update_logger(f"Plot {category} settings")

    def mode_state_changed(self):
        freq_range_objects = [
            self.range_mode_selection_combo_widget,
            self.center_freq_widget,
            self.num_freq_widget,
            self.fft_bandwidth_widget,
            self.max_range_widget,
            self.range_res_widget,
        ]
        az_objects = [
            self.azimuth_mode_selection_combo_widget,
            self.aspect_angle_phi_widget,
            self.num_inc_phi_widget,
            self.max_cross_range_az_widget,
            self.cross_range_az_res_widget,
            self.azimuth_divider,
        ]
        el_objects = [
            self.elevation_mode_selection_combo_widget,
            self.aspect_angle_theta_widget,
            self.num_inc_theta_widget,
            self.max_cross_range_el_widget,
            self.cross_range_el_res_widget,
            self.elevation_divider,
        ]

        def show(obj, show):
            if isinstance(obj, QHBoxLayout):
                for i in range(obj.count()):
                    widget = obj.itemAt(i).widget()
                    if not widget:
                        continue
                    if show:
                        widget.show()
                    else:
                        widget.hide()
            else:
                if show:
                    obj.show()
                else:
                    obj.hide()

        selected_mode = self.mode_selection_combobox.currentText()
        if "ISAR" in selected_mode:
            [show(each, True) for each in freq_range_objects]
            [show(each, True) for each in az_objects]
            [show(each, "3D" in selected_mode) for each in el_objects]
        else:
            [show(each, True) for each in freq_range_objects]
            [show(each, False) for each in az_objects]
            [show(each, False) for each in el_objects]

        # change editing settings for range
        range_mode = self.range_mode_selection_combobox.currentText()
        system_objects = [
            self.fft_bandwidth_label,
            self.fft_bandwidth_textbox,
            self.num_freq_label,
            self.num_freq_textbox,
        ]
        perf_objects = [
            self.max_range_label,
            self.max_range_textbox,
            self.range_res_label,
            self.range_res_textbox,
        ]

        for each in system_objects:
            if not isinstance(each, PyLineEditWithFloat):
                continue
            is_enabled = range_mode == "System"
            each.setEnabled(is_enabled)
            each.blocked = not is_enabled

        for each in perf_objects:
            if not isinstance(each, PyLineEditWithFloat):
                continue
            is_enabled = range_mode != "System"
            each.setEnabled(is_enabled)
            each.blocked = not is_enabled

        # change editing settings for azimuth
        azimuth_mode = self.azimuth_mode_selection_combobox.currentText()
        system_objects = [
            self.aspect_angle_phi_label,
            self.aspect_angle_phi_textbox,
            self.num_inc_phi_label,
            self.num_inc_phi_textbox,
        ]
        perf_objects = [
            self.max_cross_range_az_label,
            self.max_cross_range_az_textbox,
            self.cross_range_az_res_label,
            self.cross_range_az_res_textbox,
        ]

        for each in system_objects:
            if not isinstance(each, PyLineEditWithFloat):
                continue
            is_enabled = azimuth_mode == "System"
            each.setEnabled(is_enabled)
            each.blocked = not is_enabled

        for each in perf_objects:
            if not isinstance(each, PyLineEditWithFloat):
                continue
            is_enabled = azimuth_mode != "System"
            each.setEnabled(is_enabled)
            each.blocked = not is_enabled

        # change editing settings for elevation
        elevation_mode = self.elevation_mode_selection_combobox.currentText()
        system_objects = [
            self.aspect_angle_theta_label,
            self.aspect_angle_theta_textbox,
            self.num_inc_theta_label,
            self.num_inc_theta_textbox,
        ]
        perf_objects = [
            self.max_cross_range_el_label,
            self.max_cross_range_el_textbox,
            self.cross_range_el_res_label,
            self.cross_range_el_res_textbox,
        ]

        for each in system_objects:
            if not isinstance(each, PyLineEditWithFloat):
                continue
            is_enabled = elevation_mode == "System"
            each.setEnabled(is_enabled)
            each.blocked = not is_enabled

        for each in perf_objects:
            if not isinstance(each, PyLineEditWithFloat):
                continue
            is_enabled = elevation_mode != "System"
            each.setEnabled(is_enabled)
            each.blocked = not is_enabled

        # change for RCS. RCS does not allow plotting range/cross range post-processed
        # quantities. The modes should be set to system, and the range/cross range
        # parts disabled
        show(self.preview_toggle, True)
        show(self.show_preview_label, True)

        if self.main_window.incident_wave_menu.preview_toggle.isChecked():
            self.main_window.incident_wave_menu.show_arrow_preview()
        if self.preview_toggle.isChecked():
            self.show_preview()

    def update_center_freq(self):
        if self.range_mode_selection_combobox.currentText() == "System":
            self.update_range_sys2perf()
        else:
            self.update_range_perf2sys()
        if self.azimuth_mode_selection_combobox.currentText() == "System":
            self.update_crossrange_az_sys2perf()
        else:
            self.update_crossrange_az_perf2sys()
        if self.elevation_mode_selection_combobox.currentText() == "System":
            self.update_crossrange_el_sys2perf()
        else:
            self.update_crossrange_el_perf2sys()
        # preview is handled by one of those four methods above

    def update_range_sys2perf(self):
        center_freq_text = self.center_freq_textbox.text_full_precision()
        center_freq_hz = unit_converter_rcs(value=center_freq_text, new_units="Hz", default_unit_system="Freq")
        fft_bandwidth_hz = unit_converter_rcs(value=self.fft_bandwidth_textbox.text_full_precision(), new_units="Hz", default_unit_system="Freq")
        num_freq = self.num_freq_textbox.value
        freq_domain = DomainTransforms.fft_bandwidth_to_freq_domain(fft_bandwidth_hz, center_freq_hz, num_freq)
        dt = DomainTransforms(freq_domain=freq_domain)
        self.sim_freq_lower = dt.freq_domain[0]
        self.sim_freq_upper = dt.freq_domain[-1]
        self.max_range_textbox.set_value_unit_text(value=dt.range_period, unit="m")
        self.range_res_textbox.set_value_unit_text(value=dt.range_resolution, unit="m")
        if self.main_window.incident_wave_menu.preview_toggle.isChecked():
            self.main_window.incident_wave_menu.show_arrow_preview()
        if self.preview_toggle.isChecked():
            self.show_preview()

    def update_range_perf2sys(self):
        center_freq_hz = unit_converter_rcs(value=self.center_freq_textbox.text_full_precision(), new_units="Hz",
                                             default_unit_system="Freq")
        range_max_tgt = unit_converter_rcs(value=self.max_range_textbox.text_full_precision(), new_units="m")
        range_res_tgt = unit_converter_rcs(value=self.range_res_textbox.text_full_precision(), new_units="m")
        num_range = int(np.ceil(range_max_tgt / range_res_tgt))

        range_domain = np.linspace(0, range_res_tgt * (num_range - 1), num=num_range)
        dt = DomainTransforms(range_domain=range_domain, center_freq=center_freq_hz)
        self.sim_freq_lower = dt.freq_domain[0]
        self.sim_freq_upper = dt.freq_domain[-1]
        bw = unit_converter_rcs(value=str(dt.fft_bandwidth) + "Hz", new_units="GHz")
        self.fft_bandwidth_textbox.set_value_unit_text(value=bw, unit="GHz")
        self.num_freq_textbox.set_value_unit_text(value=dt.num_freq, unit="")
        self.max_range_textbox.set_value_unit_text(value=dt.range_period, unit="m")
        self.range_res_textbox.set_value_unit_text(value=dt.range_resolution, unit="m")
        if self.main_window.incident_wave_menu.preview_toggle.isChecked():
            self.main_window.incident_wave_menu.show_arrow_preview()
        if self.preview_toggle.isChecked():
            self.show_preview()

    def update_crossrange_az_sys2perf(self):
        self.update_crossrange_sys2perf(cut="AZ")

    def update_crossrange_az_perf2sys(self):
        self.update_crossrange_perf2sys(cut="AZ")

    def update_crossrange_el_sys2perf(self):
        self.update_crossrange_sys2perf(cut="EL")

    def update_crossrange_el_perf2sys(self):
        self.update_crossrange_perf2sys(cut="EL")

    def update_crossrange_sys2perf(self, cut):
        center_freq = self.center_freq_textbox.text_full_precision()
        center_freq_hz = unit_converter_rcs(value=center_freq, new_units="Hz")
        # the definition of bandwidth includes the df/2 tails at the extrema of the interval, like in ADP
        if cut == "AZ":
            num_inc_phi = self.num_inc_phi_textbox.value
            aspect_ang_phi = unit_converter_rcs(
                value=self.aspect_angle_phi_textbox.text_full_precision(), new_units="deg"
            )
            aspect_domain = np.linspace(-aspect_ang_phi / 2, aspect_ang_phi / 2, num=num_inc_phi)
        else:
            num_inc_theta = self.num_inc_theta_textbox.value
            aspect_ang_theta = unit_converter_rcs(
                value=self.aspect_angle_theta_textbox.text_full_precision(), new_units="deg"
            )
            aspect_domain = np.linspace(-aspect_ang_theta / 2, aspect_ang_theta / 2, num=num_inc_theta)
        dt = DomainTransforms(aspect_domain=aspect_domain, center_freq=center_freq_hz)
        if cut == "AZ":
            self.max_cross_range_az_textbox.set_value_unit_text(value=dt.range_period, unit="m")
            self.cross_range_az_res_textbox.set_value_unit_text(value=dt.range_resolution, unit="m")
        else:
            self.max_cross_range_el_textbox.set_value_unit_text(value=dt.range_period, unit="m")
            self.cross_range_el_res_textbox.set_value_unit_text(value=dt.range_resolution, unit="m")

        if self.main_window.incident_wave_menu.preview_toggle.isChecked():
            self.main_window.incident_wave_menu.show_arrow_preview()
        if self.preview_toggle.isChecked():
            self.show_preview()

    def update_crossrange_perf2sys(self, cut):
        center_freq_hz = unit_converter_rcs(value=self.center_freq_textbox.text_full_precision(), new_units="Hz")
        if cut == "AZ":
            range_max_tgt = unit_converter_rcs(value=self.max_cross_range_az_textbox.text_full_precision(),
                                               new_units="m")
            range_res_tgt = unit_converter_rcs(value=self.cross_range_az_res_textbox.text_full_precision(),
                                               new_units="m")
        else:
            range_max_tgt = unit_converter_rcs(value=self.max_cross_range_el_textbox.text_full_precision(),
                                               new_units="m")
            range_res_tgt = unit_converter_rcs(value=self.cross_range_el_res_textbox.text_full_precision(),
                                               new_units="m")
        num_range = int(np.ceil(range_max_tgt / range_res_tgt))
        range_domain = np.linspace(0, range_res_tgt * (num_range - 1), num=num_range)
        dt = DomainTransforms(range_domain=range_domain, center_freq=center_freq_hz)

        if cut == "AZ":
            self.aspect_angle_phi_textbox.set_value_unit_text(value=dt.aspect_angle, unit="deg")
            self.num_inc_phi_textbox.set_value_unit_text(value=dt.num_aspect_angle, unit="")
            self.max_cross_range_az_textbox.set_value_unit_text(value=dt.range_period, unit="m")
            self.cross_range_az_res_textbox.set_value_unit_text(value=dt.range_resolution, unit="m")
        else:
            self.aspect_angle_theta_textbox.set_value_unit_text(value=dt.aspect_angle, unit="deg")
            self.num_inc_theta_textbox.set_value_unit_text(value=dt.num_aspect_angle, unit="")
            self.max_cross_range_el_textbox.set_value_unit_text(value=dt.range_period, unit="m")
            self.cross_range_el_res_textbox.set_value_unit_text(value=dt.range_resolution, unit="m")
        if self.main_window.incident_wave_menu.preview_toggle.isChecked():
            self.main_window.incident_wave_menu.show_arrow_preview()
        if self.preview_toggle.isChecked():
            self.show_preview()

    def set_options_enabled(self, enabled: bool = False):
        self.mode_selection_combobox.blockSignals(not enabled)
        self.mode_selection_combobox.setEnabled(enabled)
        self.mode_state_changed()

        self.center_freq_textbox.blockSignals(not enabled)
        self.center_freq_textbox.setEnabled(enabled)
        self.center_freq_textbox.blocked = not enabled

        # Range
        self.range_mode_selection_combobox.blockSignals(not enabled)
        self.range_mode_selection_combobox.setEnabled(enabled)

        self.fft_bandwidth_textbox.blockSignals(not enabled)
        self.fft_bandwidth_textbox.setEnabled(enabled)
        self.fft_bandwidth_textbox.blocked = not enabled

        self.num_freq_textbox.blockSignals(not enabled)
        self.num_freq_textbox.setEnabled(enabled)
        self.num_freq_textbox.blocked = not enabled

        self.max_range_textbox.blockSignals(not enabled)
        self.max_range_textbox.setEnabled(enabled)
        self.max_range_textbox.blocked = not enabled

        self.range_res_textbox.blockSignals(not enabled)
        self.range_res_textbox.setEnabled(enabled)
        self.range_res_textbox.blocked = not enabled

        # Azimuth
        self.azimuth_mode_selection_combobox.blockSignals(not enabled)
        self.azimuth_mode_selection_combobox.setEnabled(enabled)

        self.aspect_angle_phi_textbox.blockSignals(not enabled)
        self.aspect_angle_phi_textbox.setEnabled(enabled)
        self.aspect_angle_phi_textbox.blocked = not enabled

        self.num_inc_phi_textbox.blockSignals(not enabled)
        self.num_inc_phi_textbox.setEnabled(enabled)
        self.num_inc_phi_textbox.blocked = not enabled

        self.max_cross_range_az_textbox.blockSignals(not enabled)
        self.max_cross_range_az_textbox.setEnabled(enabled)
        self.max_cross_range_az_textbox.blocked = not enabled

        self.cross_range_az_res_textbox.blockSignals(not enabled)
        self.cross_range_az_res_textbox.setEnabled(enabled)
        self.cross_range_az_res_textbox.blocked = not enabled

        # Elevation
        self.elevation_mode_selection_combobox.blockSignals(not enabled)
        self.elevation_mode_selection_combobox.setEnabled(enabled)

        self.aspect_angle_theta_textbox.blockSignals(not enabled)
        self.aspect_angle_theta_textbox.setEnabled(enabled)
        self.aspect_angle_theta_textbox.blocked = not enabled

        self.num_inc_theta_textbox.blockSignals(not enabled)
        self.num_inc_theta_textbox.setEnabled(enabled)
        self.num_inc_theta_textbox.blocked = not enabled

        self.max_cross_range_el_textbox.blockSignals(not enabled)
        self.max_cross_range_el_textbox.setEnabled(enabled)
        self.max_cross_range_el_textbox.blocked = not enabled

        self.cross_range_el_res_textbox.blockSignals(not enabled)
        self.cross_range_el_res_textbox.setEnabled(enabled)
        self.cross_range_el_res_textbox.blocked = not enabled

    def save_status(self):
        properties.radar_explorer.select_mode = self.mode_selection_combobox.currentText()
        properties.radar_explorer.center_frequency = self.center_freq_textbox.text()
        # Range
        properties.radar_explorer.range_mode = self.range_mode_selection_combobox.currentText()
        properties.radar_explorer.fft_bandwidth = f"{self.fft_bandwidth_textbox.value}{self.fft_bandwidth_textbox.unit}"
        properties.radar_explorer.frequencies = f"{self.num_freq_textbox.value}"
        properties.radar_explorer.maximum_range = f"{self.max_range_textbox.value}{self.max_range_textbox.unit}"
        properties.radar_explorer.range_resolution = f"{self.range_res_textbox.value}{self.range_res_textbox.unit}"

        # Azimuth
        properties.radar_explorer.azimuth_span = (
            f"{self.aspect_angle_phi_textbox.value}{self.aspect_angle_phi_textbox.unit}"
        )
        properties.radar_explorer.azimuth_angles = f"{self.num_inc_phi_textbox.value}"
        properties.radar_explorer.maximum_cross_range_azimuth = (
            f"{self.max_cross_range_az_textbox.value}{self.max_cross_range_az_textbox.unit}"
        )
        properties.radar_explorer.cross_range_azimuth_resolution = (
            f"{self.cross_range_az_res_textbox.value}{self.cross_range_az_res_textbox.unit}"
        )
        # Elevation
        properties.radar_explorer.elevation_span = (
            f"{self.aspect_angle_theta_textbox.value}{self.aspect_angle_theta_textbox.unit}"
        )
        properties.radar_explorer.elevation_angles = f"{self.num_inc_theta_textbox.value}"
        properties.radar_explorer.maximum_cross_range_elevation = (
            f"{self.max_cross_range_el_textbox.value}{self.max_cross_range_el_textbox.unit}"
        )
        properties.radar_explorer.cross_range_elevation_resolution = (
            f"{self.cross_range_el_res_textbox.value}{self.cross_range_el_res_textbox.unit}"
        )

    def load_status(self):
        self.set_options_enabled(False)

        self.mode_selection_combobox.setCurrentText(properties.radar_explorer.select_mode)

        center_frequency = Quantity(properties.radar_explorer.center_frequency)
        self.center_freq_textbox.precision = properties.radar_explorer.precision
        self.center_freq_textbox.set_value_unit_text(center_frequency.value, center_frequency.unit)

        self.range_mode_selection_combobox.setCurrentText(properties.radar_explorer.range_mode)

        fft_bandwidth = Quantity(properties.radar_explorer.fft_bandwidth)
        self.fft_bandwidth_textbox.precision = properties.radar_explorer.precision
        self.fft_bandwidth_textbox.set_value_unit_text(fft_bandwidth.value, fft_bandwidth.unit)

        frequencies = Quantity(properties.radar_explorer.frequencies)
        self.num_freq_textbox.precision = properties.radar_explorer.precision
        self.num_freq_textbox.set_value_unit_text(frequencies.value, frequencies.unit)

        maximum_range = Quantity(properties.radar_explorer.maximum_range)
        self.max_range_textbox.precision = properties.radar_explorer.precision
        self.max_range_textbox.set_value_unit_text(maximum_range.value, maximum_range.unit)

        range_resolution = Quantity(properties.radar_explorer.range_resolution)
        self.range_res_textbox.precision = properties.radar_explorer.precision
        self.range_res_textbox.set_value_unit_text(range_resolution.value, range_resolution.unit)

        self.azimuth_mode_selection_combobox.setCurrentText(properties.radar_explorer.azimuth_mode)

        azimuth_span = Quantity(properties.radar_explorer.azimuth_span)
        self.aspect_angle_phi_textbox.precision = properties.radar_explorer.precision
        self.aspect_angle_phi_textbox.set_value_unit_text(azimuth_span.value, azimuth_span.unit)

        azimuth_angles = Quantity(properties.radar_explorer.azimuth_angles)
        self.num_inc_phi_textbox.precision = properties.radar_explorer.precision
        self.num_inc_phi_textbox.set_value_unit_text(azimuth_angles.value, azimuth_angles.unit)

        maximum_cross_range_azimuth = Quantity(properties.radar_explorer.maximum_cross_range_azimuth)
        self.max_cross_range_az_textbox.precision = properties.radar_explorer.precision
        self.max_cross_range_az_textbox.set_value_unit_text(
            maximum_cross_range_azimuth.value, maximum_cross_range_azimuth.unit
        )

        cross_range_azimuth_resolution = Quantity(properties.radar_explorer.cross_range_azimuth_resolution)
        self.cross_range_az_res_textbox.precision = properties.radar_explorer.precision
        self.cross_range_az_res_textbox.set_value_unit_text(
            cross_range_azimuth_resolution.value, cross_range_azimuth_resolution.unit
        )

        self.elevation_mode_selection_combobox.setCurrentText(properties.radar_explorer.elevation_mode)

        elevation_span = Quantity(properties.radar_explorer.elevation_span)
        self.aspect_angle_theta_textbox.precision = properties.radar_explorer.precision
        self.aspect_angle_theta_textbox.set_value_unit_text(elevation_span.value, elevation_span.unit)

        elevation_angles = Quantity(properties.radar_explorer.elevation_angles)
        self.num_inc_theta_textbox.precision = properties.radar_explorer.precision
        self.num_inc_theta_textbox.set_value_unit_text(elevation_angles.value, elevation_angles.unit)

        maximum_cross_range_elevation = Quantity(properties.radar_explorer.maximum_cross_range_elevation)
        self.max_cross_range_el_textbox.precision = properties.radar_explorer.precision
        self.max_cross_range_el_textbox.set_value_unit_text(
            maximum_cross_range_elevation.value, maximum_cross_range_elevation.unit
        )

        cross_range_elevation_resolution = Quantity(properties.radar_explorer.cross_range_elevation_resolution)
        self.cross_range_el_res_textbox.precision = properties.radar_explorer.precision
        self.cross_range_el_res_textbox.set_value_unit_text(
            cross_range_elevation_resolution.value, cross_range_elevation_resolution.unit
        )

        self.set_options_enabled(True)

    def post_3d_settings_setup(self):
        layout_row_obj = QHBoxLayout()
        self.mode_select_column_vertical_layout.addLayout(layout_row_obj)

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

    def __preview_toggle(self):
        row_returns = self.ui.add_toggle(
            self.mode_select_column_vertical_layout,
            height=30,
            width=[135, 180, 0],
            label=["Show Preview", ""],
            font_size=self.combo_size,
            bg_color=self.app_color["label_off"],
            active_color=self.app_color["label_on"],
            text_color_on=self.app_color["text_foreground"],
            text_color_off=self.app_color["text_foreground"],
            show_on_off=True,
        )
        self.ui.left_column.menus.incident_preview_select_row = row_returns[0]
        self.show_preview_label = row_returns[1]
        self.preview_toggle = row_returns[2]
