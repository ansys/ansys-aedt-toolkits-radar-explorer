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

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QWidget

from ansys.aedt.toolkits.common import __version__
from ansys.aedt.toolkits.radar_explorer.ui.windows.help.help_column import Ui_LeftColumn
from ansys.aedt.toolkits.radar_explorer.ui.windows.help.help_page import Ui_help

ABOUT_TEXT = f"""<h2>PyAEDT Radar Explorer Toolkit {__version__}</h2>
<p>Project using <a href='https://wiki.qt.io/Qt_for_Python'> PySide6</a>, Copyright 2024 The Qt Company Ltd.</p>
<p>The graphical user interface (GUI) components are licensed under
<a href='https://www.gnu.org/licenses/lgpl-3.0.en.html'>LGPL v3.0</a>.</p>
<p>Except for the GUI components, your use of this software is governed by the Apache-2.0 License. In addition, this package
allows you to access a software that is licensed under separate terms ("Separately Licensed Software").
If you choose to install such Separately Licensed Software, you acknowledge that you are responsible for complying
with any associated terms and conditions.</p>
<p>Copyright 2024 - 2025 ANSYS, Inc. All rights reserved.</p>
<p>If you have any questions or issues, please open an issue in
<a href='https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/issues'>ansys-aedt-toolkits-radar-explorer Issues</a> page.</p>
<p>Alternatively, you can contact us at <a href='mailto:pyansys.core@ansys.com'>pyansys.core@ansys.com</a>.</p>
"""
DOCUMENTATION_URL = "https://aedt.radar.explorer.toolkit.docs.pyansys.com/"
ISSUE_TRACKER_URL = "https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/issues"


class HelpMenu(object):
    def __init__(self, main_window):
        # General properties
        self.main_window = main_window
        self.ui = main_window.ui
        self.temp_folder = tempfile.mkdtemp()

        # Add page
        plot_design_menu_index = self.ui.add_page(Ui_help)
        self.ui.load_pages.pages.setCurrentIndex(plot_design_menu_index)
        self.plot_design_menu_widget = self.ui.load_pages.pages.currentWidget()

        # Add left column
        new_column_widget = QWidget()
        new_ui = Ui_LeftColumn()
        new_ui.setupUi(new_column_widget)
        self.ui.left_column.menus.menus.addWidget(new_column_widget)
        self.plot_design_column_widget = new_column_widget
        self.plot_design_column_vertical_layout = new_ui.help_vertical_layout

        # Specific properties
        # self.plot_design_label = self.plot_design_menu_widget.findChild(QLabel, "plot_design_label")
        self.plot_design_grid = self.plot_design_menu_widget.findChild(QGridLayout, "help_grid")

        self.plot_design_button_layout = None
        self.about_button = None
        self.online_documentation_button = None
        self.issue_tracker_button = None

    def setup(self):
        # Set column

        # About button
        row_returns = self.ui.add_n_buttons(
            self.plot_design_column_vertical_layout,
            num_buttons=1,
            height=40,
            width=[200],
            text=["About"],
            font_size=self.main_window.properties.font["title_size"],
        )
        self.plot_design_button_layout = row_returns[0]
        self.about_button = row_returns[1]
        self.plot_design_button_layout.addWidget(self.about_button)
        self.about_button.clicked.connect(self.about_button_clicked)

        # Documentation button
        row_returns = self.ui.add_n_buttons(
            self.plot_design_column_vertical_layout,
            num_buttons=1,
            height=40,
            width=[200],
            text=["Documentation website"],
            font_size=self.main_window.properties.font["title_size"],
        )
        self.plot_design_button_layout = row_returns[0]
        self.online_documentation_button = row_returns[1]
        self.plot_design_button_layout.addWidget(self.online_documentation_button)
        self.online_documentation_button.clicked.connect(self.visit_website)

        # Issue tracker button
        row_returns = self.ui.add_n_buttons(
            self.plot_design_column_vertical_layout,
            num_buttons=1,
            height=40,
            width=[200],
            text=["Issue tracker"],
            font_size=self.main_window.properties.font["title_size"],
        )

        self.plot_design_button_layout = row_returns[0]
        self.issue_tracker_button = row_returns[1]
        self.plot_design_button_layout.addWidget(self.issue_tracker_button)
        self.issue_tracker_button.clicked.connect(self.report_issue)

    def about_button_clicked(self):
        """Display the PyAEDT Common Toolkit 'About' information."""
        QtWidgets.QMessageBox.about(self.main_window, "About", ABOUT_TEXT)

    def visit_website(self):
        """Access the PyAEDT Common Toolkit documentation."""
        url = QtCore.QUrl(DOCUMENTATION_URL)
        QtGui.QDesktopServices.openUrl(url)

    def report_issue(self):
        """Access the PyAEDT Common Toolkit issues tracker."""
        url = QtCore.QUrl(ISSUE_TRACKER_URL)
        QtGui.QDesktopServices.openUrl(url)
