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

from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSplashScreen

from ansys.aedt.toolkits.radar_explorer.ui.models import properties


def show_splash_screen(app):
    """
    Show the splash screen for the application.

    Creates a splash screen with a specified image and dimensions,
    displaying it for a certain duration before closing. The splash
    screen appears on top of the main application window.
    """
    if properties.high_resolution:
        splash_dim = 800
    else:  # pragma: no cover
        splash_dim = 600
    splash_pix = QPixmap(Path(__file__).parent / "splash.png")
    scaled_pix = splash_pix.scaled(splash_dim, splash_dim, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    splash = QSplashScreen(scaled_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.show()

    # Close the splash screen after a delay (e.g., 3000 milliseconds)
    QTimer.singleShot(7000, splash.close)

    # Start the main application after the splash screen
    QTimer.singleShot(7000, splash.close)
    app.processEvents()
    return splash
