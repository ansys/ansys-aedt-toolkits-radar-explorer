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

from unittest.mock import MagicMock
from unittest.mock import patch

from ansys.aedt.toolkits.radar_explorer.ui import splash


class TestSplash:
    @patch("ansys.aedt.toolkits.radar_explorer.ui.splash.properties")
    @patch("ansys.aedt.toolkits.radar_explorer.ui.splash.QTimer")
    @patch("ansys.aedt.toolkits.radar_explorer.ui.splash.QPixmap")
    @patch("ansys.aedt.toolkits.radar_explorer.ui.splash.QSplashScreen")
    @patch("ansys.aedt.toolkits.radar_explorer.ui.splash.Qt")
    def test_show_splash_screen(self, mock_qt, mock_qsplash, mock_qpixmap, mock_qtimer, mock_properties):
        mock_properties.high_resolution = True

        mock_app = MagicMock()

        mock_pixmap = MagicMock()
        mock_qpixmap.return_value = mock_pixmap
        mock_pixmap.scaled.return_value = mock_pixmap

        mock_splash = MagicMock()
        mock_qsplash.return_value = mock_splash

        splash_obj = splash.show_splash_screen(mock_app)

        mock_qpixmap.assert_called_once()
        mock_pixmap.scaled.assert_called_once_with(800, 800, mock_qt.KeepAspectRatio, mock_qt.SmoothTransformation)

        mock_qsplash.assert_called_once_with(mock_pixmap, mock_qt.WindowStaysOnTopHint)

        mock_splash.setWindowFlag.assert_called_once_with(mock_qt.FramelessWindowHint)

        mock_splash.show.assert_called_once()

        assert mock_qtimer.singleShot.call_count == 2
        mock_qtimer.singleShot.assert_any_call(7000, mock_splash.close)

        mock_app.processEvents.assert_called_once()

        assert splash_obj == mock_splash
