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

from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import ansys.aedt.toolkits.radar_explorer.backend.run_backend as backend_module
from ansys.aedt.toolkits.radar_explorer.backend.run_backend import run_backend

pytestmark = [pytest.mark.rest_api_toolkit]


class TestRunBackend:
    @patch("ansys.aedt.toolkits.radar_explorer.backend.run_backend.MultithreadingServer")
    def test_run_backend_calls_server_run(self, mock_server_class):
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        with patch("ansys.aedt.toolkits.radar_explorer.backend.run_backend.toolkit_api") as mock_api:
            mock_api.properties.debug = False
            mock_api.properties.port = 12345
            mock_api.properties.url = "localhost"
            run_backend(12345)
            mock_server.run.assert_called_once_with(host="localhost", port=12345, app=ANY)

    @pytest.mark.run_utils
    def test_export_rcs_ok_request_json(self):
        app = backend_module.app
        # Simula una petición GET con body JSON (si tu handler usa request.json)
        with app.test_request_context(
            "/export_rcs",
            method="GET",
            json={"excitation": "ex", "expression": "expr", "encode": True},
        ):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.export_rcs.return_value = {"result": "ok"}
                resp, code = backend_module.export_rcs()

        assert code == 200
        assert resp.get_json() == str({"result": "ok"})
        mock_toolkit.export_rcs.assert_called_once_with(excitation="ex", expression="expr", encode=True)

    @pytest.mark.run_utils
    def test_get_setups_ok(self):
        app = backend_module.app
        with app.test_request_context("/get_setups", method="GET"):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.get_setups.return_value = "setups"
                resp = backend_module.get_setups()
        assert resp == "setups"
        mock_toolkit.get_setups.assert_called_once()

    @pytest.mark.run_utils
    def test_get_materials_ok(self):
        app = backend_module.app
        with app.test_request_context("/get_materials", method="GET"):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.get_materials.return_value = "materials"
                resp = backend_module.get_materials()
        assert resp == "materials"
        mock_toolkit.get_materials.assert_called_once()

    @pytest.mark.run_utils
    def test_get_plane_waves_ok(self):
        app = backend_module.app
        with app.test_request_context("/get_plane_waves", method="GET"):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.get_plane_waves.return_value = "waves"
                resp = backend_module.get_plane_waves()
        assert resp == "waves"
        mock_toolkit.get_plane_waves.assert_called_once()

    @pytest.mark.run_utils
    def test_duplicate_sbr_design_route_ok(self):
        app = backend_module.app
        with app.test_request_context(
            "/duplicate_sbr_design",
            method="POST",
            json={"name": "design"},
        ):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.duplicate_sbr_design.return_value = "design"
                resp, code = backend_module.duplicate_sbr_design_route()
        assert code == 200
        mock_toolkit.duplicate_sbr_design.assert_called_once_with("design")

    @pytest.mark.run_utils
    def test_generate_3d_component_ok(self):
        app = backend_module.app
        with app.test_request_context("/generate_3d_component", method="GET"):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.generate_3d_component.return_value = "component"
                resp, code = backend_module.generate_3d_component()
        assert resp.get_json() == "component"
        assert code == 200
        mock_toolkit.generate_3d_component.assert_called_once()

    @pytest.mark.run_utils
    def test_insert_sbr_design_ok(self):
        app = backend_module.app
        with app.test_request_context(
            "/insert_sbr_design",
            method="GET",
            json={"input_file": "file", "name": "name"},
        ):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.insert_sbr_design.return_value = "inserted"
                resp, code = backend_module.insert_sbr_design()
        assert resp.get_json() == "inserted"
        assert code == 200
        mock_toolkit.insert_sbr_design.assert_called()

    @pytest.mark.run_utils
    def test_insert_cad_ok(self):
        app = backend_module.app
        with app.test_request_context(
            "/insert_cad",
            method="PUT",
            json={"input_file": "file", "material": "mat", "position": "pos", "extension": ".ext", "units": "mm"},
        ):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.insert_cad_sbr.return_value = "inserted"
                resp, code = backend_module.insert_cad()
        assert resp.get_json() == "inserted"
        assert code == 200
        mock_toolkit.insert_cad_sbr.assert_called()

    @pytest.mark.run_utils
    def test_add_plane_wave_ok(self):
        app = backend_module.app
        with app.test_request_context("/add_plane_wave", method="GET"):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.add_plane_wave.side_effect = ["v", "h"]
                resp, code = backend_module.add_plane_wave()
        assert resp.get_json() == ["v", "h"]
        assert code == 200
        assert mock_toolkit.add_plane_wave.call_count == 2

    @pytest.mark.run_utils
    def test_create_setup_ok(self):
        app = backend_module.app
        with app.test_request_context("/create_setup", method="GET"):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.add_setup.return_value = "setup"
                resp, code = backend_module.create_setup()
        assert resp.get_json() == "setup"
        assert code == 200
        mock_toolkit.add_setup.assert_called_once()

    @pytest.mark.run_utils
    def test_analyze_ok(self):
        app = backend_module.app
        with app.test_request_context("/analyze", method="POST"):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.analyze.return_value = True
                resp, code = backend_module.analyze()
        assert resp.get_json() == "AEDT design analysis has finished."
        assert code == 200
        mock_toolkit.analyze.assert_called_once()

    @pytest.mark.run_utils
    def test_get_sweeps_ok(self):
        app = backend_module.app
        with app.test_request_context("/get_sweeps", method="GET"):
            with patch.object(backend_module, "toolkit_api") as mock_toolkit:
                mock_toolkit.get_sweeps.return_value = ["sweeps"]
                resp = backend_module.get_sweeps()
        assert resp == ["sweeps"]
        mock_toolkit.get_sweeps.assert_called_once()
