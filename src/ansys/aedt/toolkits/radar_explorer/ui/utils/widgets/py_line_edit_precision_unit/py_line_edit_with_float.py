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

from numpy import round

from ansys.aedt.toolkits.common.ui.utils.widgets.py_line_edit.py_line_edit import PyLineEdit
from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.utils import split_num_units


class PyLineEditWithFloat(PyLineEdit):
    def __init__(
        self,
        value=1.0,
        precision=4,
        unit="m",
        val_type=float,
        place_holder_text="",
        radius=8,
        border_size=2,
        color="#FFF",
        selection_color="#FFF",
        bg_color="#333",
        bg_color_active="#222",
        context_color="#00ABE8",
        font_size=12,
    ):
        self.val_type = val_type
        self.value = self.val_type(value)
        self.precision = precision
        self.unit = unit

        self.__blocked = False
        self.radius = radius
        self.bg_color = bg_color
        self.context_color = context_color
        self.color = color
        self.selection_color = selection_color
        self.context_color = context_color
        self.bg_color_active = bg_color_active
        self.border_size = border_size
        self.font_size = font_size

        super().__init__(
            text=self._text_rounded_to_precision(),
            place_holder_text=place_holder_text,
            radius=radius,
            border_size=border_size,
            color=color,
            selection_color=selection_color,
            bg_color=bg_color,
            bg_color_active=bg_color_active,
            context_color=context_color,
            font_size=font_size,
        )

        self.editingFinished.connect(self._update_text)
        self.setToolTip(self.text_full_precision())

    @property
    def blocked(self):
        return self.__blocked

    @blocked.setter
    def blocked(self, value):
        self.__blocked = value
        self.toggle_background()

    def set_text(self, arg__1: str) -> None:
        super().setText(arg__1)
        self.setToolTip(self.text_full_precision())

    def text_full_precision(self):
        return str(self.val_type(self.value)) + self.unit

    def set_value_unit_text(self, value=1.0, unit="m"):
        self.value = value
        self.unit = unit
        self.set_text(self._text_rounded_to_precision())

    def set_background_color(self, color):
        """Set background color of QLineEdit."""
        self.set_stylesheet(
            radius=self.radius,
            border_size=self.border_size,
            color=self.color,
            selection_color=self.selection_color,
            bg_color=color,
            bg_color_active=self.bg_color_active,
            context_color=self.context_color,
            font_size=self.font_size,
        )

    def toggle_background(self):
        if self.blocked:
            self.set_background_color(self.bg_color_active)
        else:
            self.set_background_color(self.bg_color)

    def _text_rounded_to_precision(self):
        return str(self.val_type(round(self.value, self.precision))) + self.unit

    def _update_text(self) -> None:
        unit = ""
        value = self.val_type(0.0)
        text = self.text()
        try:
            value = float(text)
        except ValueError:
            is_square_units = False
            if text[-1] == "2":
                text = text.replace("2", "")
                is_square_units = True
            if "^" in text:
                text = text.replace("^", "")

            value, unit = split_num_units(text)
            if is_square_units:
                unit += "2"

        self.value = self.val_type(value)
        self.unit = unit

        self.set_text(self._text_rounded_to_precision())
