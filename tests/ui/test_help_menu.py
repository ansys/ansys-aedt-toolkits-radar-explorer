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

from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMessageBox

from ansys.aedt.toolkits.radar_explorer.ui.run_frontend import ApplicationWindow
from ansys.aedt.toolkits.radar_explorer.ui.windows.help.help_menu import ABOUT_TEXT
from ansys.aedt.toolkits.radar_explorer.ui.windows.help.help_menu import DOCUMENTATION_URL
from ansys.aedt.toolkits.radar_explorer.ui.windows.help.help_menu import ISSUE_TRACKER_URL


def test_about_button(patched_window_methods, patch_plotter, qtbot):
    """Test the about button in the help menu."""

    def check_and_close_msg_box():
        """Check the message box content and close it."""
        box = QApplication.activeWindow()
        assert "About" == box.windowTitle()
        assert ABOUT_TEXT == box.text()
        ok_button = box.button(QMessageBox.Ok)
        qtbot.mouseClick(ok_button, Qt.LeftButton)

    # Define a function to check the message box and close it after a short delay
    QTimer.singleShot(100, check_and_close_msg_box)

    window = ApplicationWindow()
    qtbot.mouseClick(window.help_menu.about_button, Qt.LeftButton)


@patch.object(QDesktopServices, "openUrl")
def test_documentation_website_button(mock_open_url, patched_window_methods, patch_plotter, qtbot):
    """Test the online documentation button in the help menu."""
    expected_arg = QUrl(DOCUMENTATION_URL)
    window = ApplicationWindow()

    qtbot.mouseClick(window.help_menu.online_documentation_button, Qt.LeftButton)

    mock_open_url.assert_called_once_with(expected_arg)


@patch.object(QDesktopServices, "openUrl")
def test_issue_tracker_button(mock_open_url, patched_window_methods, patch_plotter, qtbot):
    """Test the issue tracker button in the help menu."""
    expected_arg = QUrl(ISSUE_TRACKER_URL)
    window = ApplicationWindow()

    qtbot.mouseClick(window.help_menu.issue_tracker_button, Qt.LeftButton)

    mock_open_url.assert_called_once_with(expected_arg)
