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

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import ansys.aedt.toolkits.radar_explorer.run_toolkit as run_toolkit
from ansys.aedt.toolkits.radar_explorer.run_toolkit import show_splash_and_start_frontend
from ansys.aedt.toolkits.radar_explorer.run_toolkit import start_backend

pytestmark = [pytest.mark.run_utils]


class TestRunToolkit:
    @patch("ansys.aedt.toolkits.radar_explorer.backend.run_backend.run_backend")
    def test_start_backend(self, mock_run_backend):
        start_backend(5001)
        mock_run_backend.assert_called_once_with(5001)

    @patch("ansys.aedt.toolkits.radar_explorer.ui.splash.show_splash_screen")
    @patch("ansys.aedt.toolkits.common.utils.check_backend_communication", return_value=True)
    @patch("ansys.aedt.toolkits.radar_explorer.ui.run_frontend.run_frontend")
    def test_show_splash_and_start_frontend(self, mock_run_frontend, mock_check_backend, mock_show_splash):
        qt_app = MagicMock()
        url_backend = "http://localhost:5001"
        # Patch global variables url and port used in run_frontend
        with (
            patch("ansys.aedt.toolkits.radar_explorer.run_toolkit.url", "localhost"),
            patch("ansys.aedt.toolkits.radar_explorer.run_toolkit.port", 5001),
        ):
            show_splash_and_start_frontend(qt_app, url_backend)
            mock_show_splash.assert_called_once_with(qt_app)
            mock_run_frontend.assert_called()

    def test_terminate_processes(self):
        # Simulate backend_process with MagicMock
        backend_process = MagicMock()
        run_toolkit.backend_process = backend_process
        # Patch globals in run_toolkit
        with patch("ansys.aedt.toolkits.radar_explorer.run_toolkit.backend_process", backend_process):
            from ansys.aedt.toolkits.radar_explorer.run_toolkit import terminate_processes

            terminate_processes()
            backend_process.terminate.assert_called_once()
            backend_process.join.assert_called_once()
