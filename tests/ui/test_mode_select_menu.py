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

import math

import pytest

from ansys.aedt.toolkits.radar_explorer.ui.models import properties
from ansys.aedt.toolkits.radar_explorer.ui.run_frontend import ApplicationWindow
from ansys.aedt.toolkits.radar_explorer.ui.windows.mode.mode_menu import RANGE_MODE_LIST
from ansys.aedt.toolkits.radar_explorer.ui.windows.mode.mode_menu import SELECT_MODE_LIST

center_frequency = properties.radar_explorer.center_frequency
fft_bandwidth = properties.radar_explorer.fft_bandwidth
frequencies = properties.radar_explorer.frequencies
max_range = properties.radar_explorer.maximum_range
range_resolution = properties.radar_explorer.range_resolution
precision = properties.radar_explorer.precision


def test_mode_select_menu_default_values(patched_window_methods, qtbot, patch_plotter):
    """Test the default values of the mode selection menu in the application window."""
    windows = ApplicationWindow()
    menu = windows.mode_select_menu

    box = menu.mode_selection_combobox
    assert SELECT_MODE_LIST == [box.itemText(i) for i in range(box.count())]
    assert SELECT_MODE_LIST[0] == box.currentText()

    line = menu.center_freq_textbox
    assert center_frequency == line.text()

    box = menu.range_mode_selection_combobox
    assert RANGE_MODE_LIST == [box.itemText(i) for i in range(box.count())]
    assert RANGE_MODE_LIST[0] == box.currentText()

    line = menu.fft_bandwidth_textbox
    assert fft_bandwidth == line.text()

    line = menu.num_freq_textbox
    assert frequencies == line.text()

    line = menu.max_range_textbox
    assert max_range == line.text()

    line = menu.range_res_textbox
    assert math.isclose(
        float(range_resolution[:-1]),
        float(line.text()[:-1]),
        abs_tol=10 ** (-precision),
    )

    toggle = menu.preview_toggle
    assert not toggle.isChecked()


@pytest.mark.parametrize(
    "raw, expected_value, expected_unit, expected_text",
    [
        # plain float (no unit)
        ("3.5", 3.5, "", "3.5"),
        # with unit
        ("3GHz", 3.0, "GHz", "3.0GHz"),
        ("3 GHz", 3.0, "GHz", "3.0GHz"),
        # squared units (suffix 2 or ^2)
        ("3m2", 3.0, "m2", "3.0m2"),
        ("3m^2", 3.0, "m2", "3.0m2"),
        ("3 m ^ 2", 3.0, "m2", "3.0m2"),
    ],
)
def test_update_text_variants(
    patched_window_methods, qtbot, patch_plotter, raw, expected_value, expected_unit, expected_text
):
    windows = ApplicationWindow()
    menu = windows.mode_select_menu
    le = menu.center_freq_textbox

    le.setText(raw)
    le._update_text()

    assert le.value == expected_value
    assert le.unit == expected_unit
    assert le.text() == expected_text
