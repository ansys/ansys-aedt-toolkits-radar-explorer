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

from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.toolkits.common.ui.utils.widgets import PyIconButton
from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.utils import unit_converter_rcs
from ansys.aedt.toolkits.radar_explorer.ui.models import properties
from ansys.aedt.toolkits.radar_explorer.ui.windows.common_windows_utils import CommonWindowUtilsRCS
from ansys.aedt.toolkits.radar_explorer.ui.windows.incident_wave.incident_wave_column import Ui_LeftColumn
from ansys.aedt.toolkits.radar_explorer.ui.windows.incident_wave.incident_wave_page import Ui_Plot_Design

DEFAULT_SOLUTION_NAME_LIST = ["No solution"]
ROTATION_ORDER_LIST = ["ZYZ", "ZXZ"]


class IncidentWaveMenu(object):
    def __init__(self, main_window) -> None:
        # General properties
        self.class_name = "IncidentWaveMenu"
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
        incident_wave_menu_index = self.ui.add_page(Ui_Plot_Design)
        self.ui.load_pages.pages.setCurrentIndex(incident_wave_menu_index)
        self.incident_wave_menu_widget = self.ui.load_pages.pages.currentWidget()

        # Add left column
        new_column_widget = QWidget()
        new_ui = Ui_LeftColumn()
        new_ui.setupUi(new_column_widget)
        self.ui.left_column.menus.menus.addWidget(new_column_widget)
        self.incident_wave_column_widget = new_column_widget
        self.incident_wave_column_vertical_layout = new_ui.incident_wave_vertical_layout

        # Specific properties
        self.incident_wave_layout = self.incident_wave_menu_widget.findChild(QVBoxLayout, "plot_design_layout")

        # Mode combobox
        self.mode_selection_combo_widget = None
        self.mode_selection_label = None
        self.mode_selection_combobox = None
        self.mode_divider = None

        # Solution combobox
        self.solution_selection_combo_widget = None
        self.solution_selection_label = None
        self.solution_selection_combobox = None
        self.solution_divider = None

        # Rotation combobox
        self.rotation_combo_widget = None
        self.rotation_label = None
        self.rotation_combobox = None

        self.line1 = None

        self.angle1_widget = None
        self.angle1_label = None
        self.angle1_textbox = None

        self.angle2_widget = None
        self.angle2_label = None
        self.angle2_textbox = None

        self.angle3_widget = None
        self.angle3_label = None
        self.angle3_textbox = None

        self.line2 = None

        self.preview_toggle = None

        self.post_3d_settings_label = None
        self.post_3d_setting_icon = None
        self.line3 = None

        # Menu
        self.plotter = self.main_window.home_menu.plotter

        # Common RCS Utils
        self.rcs_utils = CommonWindowUtilsRCS(self.main_window.ui.themes)

    def setup(self):
        row_returns = self.ui.add_combobox(
            self.incident_wave_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Solution",
            combobox_list=DEFAULT_SOLUTION_NAME_LIST,
            font_size=self.combo_size,
        )

        self.solution_selection_combo_widget = row_returns[0]
        self.solution_selection_label = row_returns[1]
        self.solution_selection_combobox = row_returns[2]

        self.solution_divider = self.ui.add_vertical_line(
            self.incident_wave_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        row_returns = self.ui.add_combobox(
            self.incident_wave_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Rotation Order",
            combobox_list=ROTATION_ORDER_LIST,
            font_size=self.combo_size,
        )

        self.rotation_combo_widget = row_returns[0]
        self.rotation_label = row_returns[1]
        self.rotation_combobox = row_returns[2]

        self.rotation_combobox.currentIndexChanged.connect(self.show_arrow_preview)

        self.line1 = self.ui.add_vertical_line(
            self.incident_wave_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        # Phi
        angle1 = Quantity(properties.radar_explorer.angle1)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.incident_wave_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Phi",
            value=angle1.value,
            unit=angle1.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )

        self.angle1_widget = row_returns[0]
        self.angle1_label = row_returns[1]
        self.angle1_textbox = row_returns[2]
        self.angle1_textbox.editingFinished.connect(self.update_angle1)

        # Theta
        angle2 = Quantity(properties.radar_explorer.angle2)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.incident_wave_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Theta",
            value=angle2.value,
            unit=angle2.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )
   
        self.angle2_widget = row_returns[0]
        self.angle2_label = row_returns[1]
        self.angle2_textbox = row_returns[2]
        self.angle2_textbox.editingFinished.connect(self.update_angle2)

        # Psi
        angle3 = Quantity(properties.radar_explorer.angle3)
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.incident_wave_column_vertical_layout,
            height=40,
            width=[135, 180],
            label="Psi",
            value=angle3.value,
            unit=angle3.unit,
            precision=properties.radar_explorer.precision,
            font_size=self.combo_size,
        )

        self.angle3_widget = row_returns[0]
        self.angle3_label = row_returns[1]
        self.angle3_textbox = row_returns[2]
        self.angle3_textbox.editingFinished.connect(self.update_angle3)

        self.angle1_textbox.editingFinished.connect(self.show_arrow_preview)
        self.angle2_textbox.editingFinished.connect(self.show_arrow_preview)
        self.angle3_textbox.editingFinished.connect(self.show_arrow_preview)

        self.line2 = self.ui.add_vertical_line(
            self.incident_wave_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        self.__preview_toggle()
        self.preview_toggle.stateChanged.connect(self.show_arrow_preview)

        self.line3 = self.ui.add_vertical_line(
            self.incident_wave_column_vertical_layout, top_spacer=[0, 10], bot_spacer=[0, 10]
        )

        self.post_3d_settings_setup()

        # Page
        self.initialize_plotter()
        self.on_tab_changed()

    def on_tab_changed(self):
        if self.main_window.ui.get_selected_menu() == "incident_menu":
            self.plotter.reparent_to_placeholder(self.class_name)

    def initialize_plotter(self):
        self.plotter.add_to_window(self.class_name, self.incident_wave_layout)

    def show_arrow_preview(self):
        if self.preview_toggle.isChecked():
            category = self.main_window.mode_select_menu.mode_selection_combobox.currentText()

            phi = unit_converter_rcs(
                value=self.main_window.mode_select_menu.aspect_angle_phi_textbox.text_full_precision(), new_units="deg", 
                default_unit_system="Angle"
            )

            num_phi = int(self.main_window.mode_select_menu.num_inc_phi_textbox.text())
            theta = unit_converter_rcs(
                value=self.main_window.mode_select_menu.aspect_angle_theta_textbox.text(), new_units="deg", default_unit_system="Angle"
            )
            num_theta = int(self.main_window.mode_select_menu.num_inc_theta_textbox.text())

            solution_name = self.solution_selection_combobox.currentText()
            if solution_name == "No solution":
                rcs_object = self.ui.app.load_rcs_data_from_file()
            else:  # pragma: no cover
                rcs_objects = properties.radar_explorer.all_scene_actors["plotter"][solution_name]
                first_key = list(rcs_objects.keys())[0]
                rcs_object = rcs_objects[first_key]

            rcs_object.clear_scene()
            # properties.radar_explorer.all_scene_actors["annotations"] = None

            # TODO: fix all the annotations when we merge plotters

            if category == "Range Profile":
                rcs_object._add_incident_settings()
            elif category == "2D ISAR":
                rcs_object._add_incident_settings(phi_span=phi, num_phi=num_phi)
            elif category == "3D ISAR":
                rcs_object._add_incident_settings(theta_span=theta, num_theta=num_theta, phi_span=phi, num_phi=num_phi)
            properties.radar_explorer.all_scene_actors["annotations"]["incident_wave"] = (rcs_object.all_scene_actors)[
                "annotations"
            ]["incident_wave"]
            self.ui.update_logger(f"Plot {category} incident wave")

            if "Ansys_scene" in properties.radar_explorer.all_scene_actors["model"].keys():  # pragma: no cover
                self.main_window.home_menu.reset_scene()
        else:
            properties.radar_explorer.all_scene_actors["annotations"]["incident_wave"] = None

        self.plotter.plot_model_scene()

    def set_options_enabled(self, enabled: bool = False):
        self.angle1_textbox.setEnabled(enabled)
        self.angle1_textbox.blocked = not enabled

        self.angle2_textbox.setEnabled(enabled)
        self.angle2_textbox.blocked = not enabled

        self.angle3_textbox.setEnabled(enabled)
        self.angle3_textbox.blocked = not enabled

        self.rotation_combobox.setEnabled(enabled)

    def save_status(self):
        properties.radar_explorer.rotation = self.rotation_combobox.currentText()
        properties.radar_explorer.angle1 = f"{self.angle1_textbox.value}{self.angle1_textbox.unit}"
        properties.radar_explorer.angle2 = f"{self.angle2_textbox.value}{self.angle2_textbox.unit}"
        properties.radar_explorer.angle3 = f"{self.angle3_textbox.value}{self.angle3_textbox.unit}"

    def load_status(self):
        self.rotation_combobox.setCurrentText(properties.radar_explorer.rotation)

        angle1 = Quantity(properties.radar_explorer.angle1)
        self.angle1_textbox.precision = properties.radar_explorer.precision
        self.angle1_textbox.set_value_unit_text(angle1.value, angle1.unit)

        angle2 = Quantity(properties.radar_explorer.angle2)
        self.angle2_textbox.precision = properties.radar_explorer.precision
        self.angle2_textbox.set_value_unit_text(angle2.value, angle2.unit)

        angle3 = Quantity(properties.radar_explorer.angle3)
        self.angle3_textbox.precision = properties.radar_explorer.precision
        self.angle3_textbox.set_value_unit_text(angle3.value, angle3.unit)

    def post_3d_settings_setup(self):
        layout_row_obj = QHBoxLayout()
        self.incident_wave_column_vertical_layout.addLayout(layout_row_obj)

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

    def update_angle1(self):
        phi = unit_converter_rcs(
            value=self.angle1_textbox.text_full_precision(), new_units="deg", default_unit_system="Angle"
        )
        self.angle1_textbox.set_value_unit_text(phi, "deg")

    def update_angle2(self):
        val = unit_converter_rcs(
            value=self.angle2_textbox.text_full_precision(), new_units="deg", default_unit_system="Angle"
        )
        self.angle2_textbox.set_value_unit_text(val, "deg")

    def update_angle3(self):
        val = unit_converter_rcs(
            value=self.angle3_textbox.text_full_precision(), new_units="deg", default_unit_system="Angle"
        )
        self.angle3_textbox.set_value_unit_text(val, "deg")

    def __preview_toggle(self):
        row_returns = self.ui.add_toggle(
            self.incident_wave_column_vertical_layout,
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
