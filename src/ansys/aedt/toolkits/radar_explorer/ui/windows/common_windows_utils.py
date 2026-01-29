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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout

from ansys.aedt.toolkits.common.ui.utils.windows.common_window_utils import CommonWindowUtils
from ansys.aedt.toolkits.radar_explorer.ui.utils.widgets.py_line_edit_precision_unit.py_line_edit_with_float import (
    PyLineEditWithFloat,
)


class CommonWindowUtilsRCS(CommonWindowUtils):
    """Class representing a common window with various UI functionalities."""

    def __init__(self, themes):
        super().__init__()
        self.themes = themes

    def add_textbox_prec_unit(
        self,
        layout,
        height=40,
        width=None,
        label="label1",
        val_type=float,
        value=1.0,
        precision=4,
        unit="m",
        font_size=12,
    ):
        """
        Add a label and textbox for a number with a unit to a layout.

        Parameters
        ----------
        layout: QLayout
            The layout object to which the label and combobox will be added.
        height: int, optional
            The height of the label and combobox widgets. Default is 40.
        width: list, optional
            The width of the label and combobox widgets. If not provided, a default width of [100, 100] will be used.
        label: str, optional
            The text to be displayed on the label widget. Default is '"label1"'.
        val_type: type
            The type of the value to be displayed in the textbox. Default is float.
        value: float, optional
            The initial value to be displayed in the textbox. Default is 1.0.
        precision: int, optional
            The number of decimal places to display in the textbox. Default is 4.
        unit: str, optional
            The unit to be displayed in the textbox. Default is "m".
        font_size: int, optional
            The font size of the label widget. Default is 12.

        Returns
        -------
        list
            A list containing the layout row object, label object, and combobox object.
        """
        width = width or [100, 100]

        app_color = self.themes["app_color"]
        text_foreground = app_color["text_foreground"]
        bg_color = app_color["combo_color"]

        layout_row = QHBoxLayout()
        layout.addLayout(layout_row)

        label_widget = self._create_label(
            text=label,
            font_size=font_size,
            height=height,
            width=width[0],
            color=text_foreground,
        )
        layout_row.addWidget(label_widget)

        linebox_widget = PyLineEditWithFloat(
            value=value,
            precision=precision,
            unit=unit,
            val_type=val_type,
            radius=8,
            bg_color=bg_color,
            color=text_foreground,
            selection_color=app_color["white"],
            bg_color_active=app_color["dark_three"],
            context_color=app_color["context_color"],
            font_size=font_size,
        )
        linebox_widget.setMinimumHeight(height)
        linebox_widget.setFixedWidth(width[1])
        layout_row.addWidget(linebox_widget, alignment=Qt.AlignVCenter | Qt.AlignRight)

        label_widget.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        return [layout_row, label_widget, linebox_widget]

    @classmethod
    def set_visible_post_proc(cls, frontend, visible: bool, rcs_object=None):
        frontend.ui.left_menu.set_visible_button("post_2d_menu", visible)
        frontend.ui.left_menu.set_visible_button("post_3d_menu", visible)
        if visible:
            if rcs_object is None:
                raise Exception("No results found during prosessing.")
            data = next(iter(rcs_object.values())).rcs_data
            num_freq = len(data.frequencies)
            num_theta = len(data.available_incident_wave_theta)
            num_phi = len(data.available_incident_wave_phi)
            if num_freq == 1:
                # Single frequency, no post processing
                combo_3d = frontend.main_window.post_3d_menu.category_combobox
                combo_3d.blockSignals(True)
                combo_3d.clear()
                combo_3d.addItems(["RCS"])
                combo_3d.blockSignals(False)
                combo_3d.setCurrentText("RCS")
                combo_2d = frontend.main_window.post_2d_menu.category_combobox
                combo_2d.blockSignals(True)
                combo_2d.clear()
                combo_2d.addItems(["RCS"])
                combo_2d.blockSignals(False)
                combo_2d.setCurrentText("RCS")
                return
            if num_phi > 1 and num_theta > 1:
                # set deafult 3D ISAR
                combo_3d = frontend.main_window.post_3d_menu.category_combobox
                combo_3d.blockSignals(True)
                combo_3d.clear()
                combo_3d.addItems(["RCS", "Range Profile", "Waterfall", "2D ISAR", "3D ISAR"])
                combo_3d.blockSignals(False)
                combo_3d.setCurrentText("3D ISAR")

                combo_2d = frontend.main_window.post_2d_menu.category_combobox
                combo_2d.blockSignals(True)
                combo_2d.clear()
                combo_2d.addItems(["RCS", "Range Profile", "Waterfall", "2D ISAR", "3D ISAR"])
                combo_2d.blockSignals(False)
                combo_2d.setCurrentText("3D ISAR")
            elif num_phi > 1 or num_theta > 1:
                # set default 2D ISAR
                # 3D Post processing
                combo_3d = frontend.main_window.post_3d_menu.category_combobox
                combo_3d.blockSignals(True)
                combo_3d.clear()
                combo_3d.addItems(["RCS", "Range Profile", "Waterfall", "2D ISAR"])
                combo_3d.blockSignals(False)
                combo_3d.setCurrentText("2D ISAR")
                # 2D Post processing
                combo_2d = frontend.main_window.post_2d_menu.category_combobox
                combo_2d.blockSignals(True)
                combo_2d.clear()
                combo_2d.addItems(["RCS", "Range Profile", "Waterfall", "2D ISAR"])
                combo_2d.blockSignals(False)
                combo_2d.setCurrentText("2D ISAR")
            else:
                # set default Range Profile
                # 3D Post processing
                combo_3d = frontend.main_window.post_3d_menu.category_combobox
                combo_3d.blockSignals(True)
                combo_3d.clear()
                combo_3d.addItems(["RCS", "Range Profile"])
                combo_3d.blockSignals(False)
                combo_3d.setCurrentText("Range Profile")
                # 2D Post processing
                combo_2d = frontend.main_window.post_2d_menu.category_combobox
                combo_2d.blockSignals(True)
                combo_2d.clear()
                combo_2d.addItems(["RCS", "Range Profile"])
                combo_2d.blockSignals(False)
                combo_2d.setCurrentText("Range Profile")
