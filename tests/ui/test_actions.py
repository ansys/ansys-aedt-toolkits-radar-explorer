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

import base64
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import ansys.aedt.toolkits.radar_explorer.ui.actions as frontend_mod


def make_rcs_ui():
    """Build a minimal set of UI stubs used by rcs_setup."""
    mode = SimpleNamespace(
        max_range_textbox=_tb("100 m"),
        range_res_textbox=_tb("2 m"),
        mode_selection_combobox=_cb_text("Monostatic"),
        aspect_angle_phi_textbox=_tb("15 deg"),
        num_inc_phi_textbox=_tb("4"),
        max_cross_range_az_textbox=_tb("30 m"),
        cross_range_az_res_textbox=_tb("0.5 m"),
        aspect_angle_theta_textbox=_tb("10 deg"),
        num_inc_theta_textbox=_tb("5"),
        max_cross_range_el_textbox=_tb("25 m"),
        cross_range_el_res_textbox=_tb("0.4 m"),
        center_freq_textbox=_tb("10 GHz"),
        fft_bandwidth_textbox=_tb("200 MHz"),
        sim_freq_lower=1.0,
        sim_freq_upper=2.0,
        num_freq_textbox=_tb("301"),
    )
    solver = SimpleNamespace(
        toggle=_chk(True),
        ray_density_textbox=_tb("0.75"),
        num_bounces_textbox=_tb("3"),
        ptd_utd=_chk(True),
        solve_interactive=_chk(False),
        cores_textbox=_tb("8"),
    )
    incident = SimpleNamespace(
        angle1_textbox=_tb("0 deg"),
        angle2_textbox=_tb("45 deg"),
        angle3_textbox=_tb("90 deg"),
        rotation_combobox=_cb_text("ZYX"),
    )
    return mode, solver, incident


def _tb(val):
    return SimpleNamespace(text=lambda: val)


def _cb_text(val):
    return SimpleNamespace(currentText=lambda: val)


def _chk(val):
    return SimpleNamespace(isChecked=lambda: val)


class MockQuantity:
    """Tiny Quantity stub for rcs_setup tests."""

    def __init__(self, s):
        self._s = str(s)

    @property
    def value(self):
        import re

        m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", self._s)
        return float(m.group(0)) if m else 0.0

    def to(self, _):
        return self


class TestActions:
    @pytest.fixture(scope="class")
    def fe(self):
        """Shared Frontend instance with a stable URL."""
        obj = frontend_mod.Frontend()
        obj.url = "http://dummy"
        return obj

    @pytest.fixture
    def patch_read_json(self, monkeypatch):
        """Replace read_json with a simple JSON file reader used by the code under test."""

        def _read_json(path_like):
            p = Path(path_like)
            return json.loads(p.read_text())

        monkeypatch.setattr(frontend_mod, "read_json", _read_json)

    def test_load_rcs_none_returns_new_plotter(self):
        with patch("ansys.aedt.toolkits.radar_explorer.ui.actions.MonostaticRCSPlotter") as mock_plotter:
            result = frontend_mod.Frontend.load_rcs_data_from_file(input_file=None)

        assert result == mock_plotter.return_value
        mock_plotter.assert_called_once_with()

    def test_load_rcs_missing_file_logs_and_false(self, tmp_path):
        missing = tmp_path / "does_not_exist.json"

        with (
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.MonostaticRCSPlotter") as mock_plotter,
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = frontend_mod.Frontend.load_rcs_data_from_file(str(missing))

        assert result is False
        mock_logger.error.assert_called_once_with("File does not exist")
        mock_plotter.assert_not_called()

    def test_load_rcs_existing_builds_data_and_plotter(self, tmp_path):
        data_file = tmp_path / "sample.json"
        data_file.write_text("{}")

        with (
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.MonostaticRCSData") as mock_rcs_data,
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.MonostaticRCSPlotter") as mock_plotter,
        ):
            result = frontend_mod.Frontend.load_rcs_data_from_file(str(data_file))

        mock_rcs_data.assert_called_once_with(input_file=str(data_file))
        mock_plotter.assert_called_once_with(rcs_data=mock_rcs_data.return_value)
        assert result == mock_plotter.return_value

    def test_get_setups_no_active_project(self, fe):
        with patch.object(fe, "get_properties", return_value={"active_project": False, "project_list": ["p1"]}):
            result = fe.get_setups()
        assert result == ["No Setup"]

    def test_get_setups_no_project_list(self, fe):
        with patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": []}):
            result = fe.get_setups()
        assert result == ["No Setup"]

    def test_get_setups_ok_response(self, fe):
        mock_resp = MagicMock(ok=True)
        mock_resp.json.return_value = ["Setup1", "Setup2"]

        with (
            patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": ["p1"]}),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp) as mock_get,
        ):
            result = fe.get_setups()

        assert result == ["Setup1", "Setup2"]
        mock_get.assert_called_once_with(
            fe.url + "/get_setups",
            timeout=frontend_mod.DEFAULT_REQUESTS_TIMEOUT,
        )
        mock_resp.json.assert_called_once()

    def test_get_setups_not_ok_response(self, fe):
        mock_resp = MagicMock(ok=False)

        with (
            patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": ["p1"]}),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp),
        ):
            result = fe.get_setups()

        assert result == ["No Setup"]

    def test_get_setups_dict_json_coerces_to_keys(self, fe):
        mock_resp = MagicMock(ok=True)
        mock_resp.json.return_value = {"S1": 1, "S2": 2}

        with (
            patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": ["p1"]}),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp),
        ):
            result = fe.get_setups()

        assert set(result) == {"S1", "S2"}

    def test_get_plane_waves_no_active_project(self, fe):
        with patch.object(fe, "get_properties", return_value={"active_project": False, "project_list": ["p1"]}):
            result = fe.get_plane_waves()
        assert result == ["No Setup"]

    def test_get_plane_waves_no_project_list(self, fe):
        with patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": []}):
            result = fe.get_plane_waves()
        assert result == ["No Setup"]

    def test_get_plane_waves_ok_response(self, fe):
        mock_resp = MagicMock(ok=True)
        mock_resp.json.return_value = ["PW1", "PW2"]

        with (
            patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": ["p1"]}),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp) as mock_get,
        ):
            result = fe.get_plane_waves()

        assert result == ["PW1", "PW2"]
        mock_get.assert_called_once_with(
            fe.url + "/get_plane_waves",
            timeout=frontend_mod.DEFAULT_REQUESTS_TIMEOUT,
        )
        mock_resp.json.assert_called_once()

    def test_get_plane_waves_not_ok_response(self, fe):
        mock_resp = MagicMock(ok=False)

        with (
            patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": ["p1"]}),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp),
        ):
            result = fe.get_plane_waves()

        assert result == ["No Setup"]

    def test_get_plane_waves_dict_json_coerces_to_keys(self, fe):
        mock_resp = MagicMock(ok=True)
        mock_resp.json.return_value = {"P1": 1, "P2": 2}

        with (
            patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": ["p1"]}),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp),
        ):
            result = fe.get_plane_waves()

        assert set(result) == {"P1", "P2"}

    def test_local_ok_geometry_only_logs_and_returns_path(self, fe, tmp_path, patch_read_json):
        # Prepare a real metadata file the function will pass to read_json later
        metadata_path = tmp_path / "meta.json"
        metadata_path.write_text(json.dumps({"monostatic_file": None, "model_info": {}}))

        resp = MagicMock(ok=True)
        resp.json.return_value = metadata_path

        with (
            patch.object(fe, "properties", SimpleNamespace(backend_url="localhost"), create=True),
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=resp) as mock_get,
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.export_rcs()

        expected_values = {"excitation": None, "expression": None, "encode": False}
        mock_get.assert_called_once_with(fe.url + "/export_rcs", json=expected_values)

        assert result == metadata_path
        mock_logger.debug.assert_called_once_with("Geometry was extracted.")

    def test_local_ok_with_monostatic_logs_filename(self, fe, tmp_path, patch_read_json):
        metadata_path = tmp_path / "meta.json"
        metadata_path.write_text(json.dumps({"monostatic_file": "result.rcs", "model_info": {}}))

        resp = MagicMock(ok=True)
        resp.json.return_value = metadata_path

        with (
            patch.object(fe, "properties", SimpleNamespace(backend_url="127.0.0.1"), create=True),
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=resp),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.export_rcs(excitation="EXC1")

        assert result == metadata_path
        mock_logger.debug.assert_called_once_with("Geometry and radar results were extracted from result.rcs.")

    def test_remote_ok_writes_files_and_logs_with_results(self, fe, tmp_path, patch_read_json):
        new_temp = tmp_path / "fresh_temp_dir"
        fe.temp_folder = str(new_temp)

        metadata = {
            "monostatic_file": "mono.rcs",
            "model_info": {"geomA": {}, "geomB": {}},
        }
        encoded_meta = base64.b64encode(json.dumps(metadata).encode()).decode()
        encoded_geom = [base64.b64encode(b"objA").decode(), base64.b64encode(b"objB").decode()]
        encoded_rcs = base64.b64encode(b"rcsdata").decode()

        resp = MagicMock(ok=True)
        resp.json.return_value = [encoded_meta, encoded_geom, encoded_rcs]

        with (
            patch.object(fe, "properties", SimpleNamespace(backend_url="remote-host"), create=True),
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=resp) as mock_get,
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.export_rcs(excitation="EXC1")

        mock_get.assert_called_once_with(
            fe.url + "/export_rcs",
            json={"excitation": "EXC1", "expression": None, "encode": True},
        )

        expected_meta_path = Path(fe.temp_folder) / "pyaedt_rcs_metadata.json"
        assert result == expected_meta_path and expected_meta_path.exists()

        geom_dir = Path(fe.temp_folder) / "geometry"
        assert (geom_dir / "geomA.obj").exists()
        assert (geom_dir / "geomB.obj").exists()
        assert (Path(fe.temp_folder) / "mono.rcs").exists()

        mock_logger.debug.assert_called_once_with("Geometry and radar results were extracted from mono.rcs.")

    def test_remote_not_ok_logs_error_and_returns_false(self, fe):
        resp = MagicMock(ok=False)

        with (
            patch.object(fe, "properties", SimpleNamespace(backend_url="remote-host"), create=True),
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=resp),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.export_rcs()

        assert result is False
        mock_logger.error.assert_called_once_with("RCS was not extracted")

    def test_release_desktop_posts_and_returns_true(self, fe):
        with patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.post") as mock_post:
            result = fe.release_desktop(close_projects=False, close_on_exit=False)

        mock_post.assert_called_once_with(
            fe.url + "/close_aedt",
            json={"close_projects": False, "close_on_exit": False},
            timeout=frontend_mod.DEFAULT_REQUESTS_TIMEOUT,
        )
        assert result is True

    def test_generate_3d_component_ok_returns_file_and_logs(self, fe):
        mock_resp = MagicMock(ok=True)
        mock_resp.json.return_value = "component.a3dcomp"

        with (
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.generate_3d_component()

        assert result == "component.a3dcomp"
        mock_logger.debug.assert_called_once_with("3D component was generated.")

    def test_generate_3d_component_not_ok_returns_false_and_logs_error(self, fe):
        mock_resp = MagicMock(ok=False)

        with (
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.generate_3d_component()

        assert result is False
        mock_logger.error.assert_called_once_with("3D component generation failed.")

    def test_insert_sbr_design_ok(self, fe):
        resp = MagicMock(ok=True)
        with (
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=resp) as mock_get,
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.insert_sbr_design(component_file="comp.a3dcomp", design_name="RCS_Design")

        assert result is True
        mock_get.assert_called_once_with(
            fe.url + "/insert_sbr_design",
            json={"input_file": "comp.a3dcomp", "name": "RCS_Design"},
        )
        mock_logger.debug.assert_called_once_with("Component inserted in new design.")

    def test_insert_sbr_design_not_ok(self, fe):
        resp = MagicMock(ok=False)
        with (
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=resp),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.insert_sbr_design(component_file="comp.a3dcomp")

        assert result is False
        mock_logger.error.assert_called_once_with("Component not inserted in new design.")

    def test_insert_cad_design_local_ok_default_position(self, fe, tmp_path):
        cad = tmp_path / "shape.obj"
        cad.write_text("dummy")
        resp = MagicMock(ok=True)

        with (
            patch.object(fe, "properties", SimpleNamespace(backend_url="localhost"), create=True),
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.put", return_value=resp) as mock_put,
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.insert_cad_design(cad)

        assert result is True
        mock_put.assert_called_once_with(
            fe.url + "/insert_cad",
            json={
                "input_file": str(cad),
                "material": "pec",
                "position": ["0.0m", "0.0m", "0.0m"],
                "extension": ".obj",
                "units": "meter",
            },
        )
        mock_logger.debug.assert_called_once_with("Component inserted in new design.")

    def test_insert_cad_design_remote_ok_custom_args(self, fe, tmp_path):
        cad = tmp_path / "shape.step"
        cad.write_text("dummy")
        resp = MagicMock(ok=True)

        with (
            patch.object(fe, "properties", SimpleNamespace(backend_url="remote-host"), create=True),
            patch.object(fe, "serialize_obj_base64", return_value=b"ZmFrZV9lbmNvZGVk"),
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.put", return_value=resp) as mock_put,
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.insert_cad_design(cad, material="copper", position=["1m", "2m", "3m"], units="mm")

        assert result is True

        mock_put.assert_called_once()
        called_json = mock_put.call_args.kwargs["json"]
        assert called_json["input_file"] == "ZmFrZV9lbmNvZGVk"
        assert called_json["material"] == "copper"
        assert called_json["position"] == ["1m", "2m", "3m"]
        assert called_json["extension"] == ".step"
        assert called_json["units"] == "mm"

        mock_logger.debug.assert_called_once_with("Component inserted in new design.")

    def test_insert_cad_design_not_ok(self, fe, tmp_path):
        cad = tmp_path / "shape.obj"
        cad.write_text("dummy")
        resp = MagicMock(ok=False)

        with (
            patch.object(fe, "properties", SimpleNamespace(backend_url="localhost"), create=True),
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.put", return_value=resp),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.insert_cad_design(cad)

        assert result is False
        mock_logger.error.assert_called_once_with("Component not inserted in new design.")

    def test_rcs_setup_happy_path(self, fe):
        mode_ui, solver_ui, inc_ui = make_rcs_ui()
        # Start properties shape
        props = {"radar": {}, "setup": {}}

        with (
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.Quantity", MockQuantity),
            patch.object(fe, "mode_select_menu", mode_ui, create=True),
            patch.object(fe, "solver_setup_menu", solver_ui, create=True),
            patch.object(fe, "incident_wave_menu", inc_ui, create=True),
            patch.object(fe, "get_properties", return_value=props),
            patch.object(fe, "set_properties", side_effect=[True, True, True]),
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get") as mock_get,
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            mock_get.side_effect = [
                MagicMock(ok=True, json=lambda: None),
                MagicMock(ok=True, json=lambda: None),
            ]

            result = fe.rcs_setup()

        assert result is True

        assert mock_get.call_count == 2
        assert mock_get.call_args_list[0].args[0].endswith("/add_plane_wave")
        assert mock_get.call_args_list[1].args[0].endswith("/create_setup")

        # Log messages
        mock_logger.debug.assert_any_call("Plane waves were created.")
        mock_logger.debug.assert_any_call("Setup was created.")

        # Properties got updated with expected keys
        assert "radar" in props and "setup" in props
        assert "range_max" in props["radar"]
        assert "center_freq" in props["setup"]

    def test_rcs_setup_fails_on_initial_set_properties(self, fe):
        mode_ui, solver_ui, inc_ui = make_rcs_ui()
        props = {"radar": {}, "setup": {}}

        with (
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.Quantity", MockQuantity),
            patch.object(fe, "mode_select_menu", mode_ui, create=True),
            patch.object(fe, "solver_setup_menu", solver_ui, create=True),
            patch.object(fe, "incident_wave_menu", inc_ui, create=True),
            patch.object(fe, "get_properties", return_value=props),
            patch.object(fe, "set_properties", return_value=False),
        ):
            assert fe.rcs_setup() is False

    def test_rcs_setup_plane_wave_creation_fails(self, fe):
        mode_ui, solver_ui, inc_ui = make_rcs_ui()
        props = {"radar": {}, "setup": {}}

        with (
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.Quantity", MockQuantity),
            patch.object(fe, "mode_select_menu", mode_ui, create=True),
            patch.object(fe, "solver_setup_menu", solver_ui, create=True),
            patch.object(fe, "incident_wave_menu", inc_ui, create=True),
            patch.object(fe, "get_properties", return_value=props),
            patch.object(fe, "set_properties", side_effect=[True, True, True]),
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch(
                "ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=MagicMock(ok=False)
            ) as mock_get,
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.rcs_setup()

        assert result is False
        mock_get.assert_called_once()
        assert mock_get.call_args.args[0].endswith("/add_plane_wave")
        mock_logger.error.assert_called_with("Plane waves creation failed.")

    def test_rcs_setup_create_setup_fails(self, fe):
        mode_ui, solver_ui, inc_ui = make_rcs_ui()
        props = {"radar": {}, "setup": {}}

        with (
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.Quantity", MockQuantity),
            patch.object(fe, "mode_select_menu", mode_ui, create=True),
            patch.object(fe, "solver_setup_menu", solver_ui, create=True),
            patch.object(fe, "incident_wave_menu", inc_ui, create=True),
            patch.object(fe, "get_properties", return_value=props),
            patch.object(fe, "set_properties", side_effect=[True, True, True]),
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get") as mock_get,
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            # add_plane_wave ok, create_setup not ok
            mock_get.side_effect = [
                MagicMock(ok=True, json=lambda: None),
                MagicMock(ok=False),
            ]

            result = fe.rcs_setup()

        assert result is False
        mock_logger.error.assert_called_with("Setup creation failed.")

    def test_analyze_ok(self, fe):
        resp = MagicMock(ok=True)
        with (
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.post", return_value=resp),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.analyze()

        assert result is True
        mock_logger.debug.assert_called_once_with("Simulation was solved.")

    def test_analyze_not_ok(self, fe):
        resp = MagicMock(ok=False)
        resp.json.return_value = "ERROR XYZ"
        with (
            patch.object(fe, "ui", SimpleNamespace(update_logger=MagicMock()), create=True),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.post", return_value=resp),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.logger") as mock_logger,
        ):
            result = fe.analyze()

        assert result is False
        mock_logger.error.assert_called_once_with("ERROR XYZ")

    def test_serialize_obj_base64(self, tmp_path):
        content = b"hello-bytes"
        f = tmp_path / "blob.bin"
        f.write_bytes(content)

        out = frontend_mod.Frontend.serialize_obj_base64(f)
        assert isinstance(out, bytes)
        assert base64.b64decode(out) == content

    def test_get_materials_ok_response(self, fe):
        mock_resp = MagicMock(ok=True)
        mock_resp.json.return_value = ["pec", "pec2"]

        with (
            patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": ["p1"]}),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp) as mock_get,
        ):
            result = fe.get_materials()

        assert result == ["pec", "pec2"]
        mock_get.assert_called_once_with(
            fe.url + "/get_materials",
            timeout=frontend_mod.DEFAULT_REQUESTS_TIMEOUT,
        )
        mock_resp.json.assert_called_once()

    def test_get_materials_not_ok_response(self, fe):
        mock_resp = MagicMock(ok=False)

        with (
            patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": ["p1"]}),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp),
        ):
            result = fe.get_materials()

        assert result == ["pec"]

    def test_get_sweeps_ok_response(self, fe):
        mock_resp = MagicMock(ok=True)
        mock_resp.json.return_value = ["sweep1", "sweep2"]

        with (
            patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": ["p1"]}),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp) as mock_get,
        ):
            result = fe.get_sweeps()

        assert result == ["sweep1", "sweep2"]
        mock_get.assert_called_once_with(
            fe.url + "/get_sweeps",
            timeout=frontend_mod.DEFAULT_REQUESTS_TIMEOUT,
        )
        mock_resp.json.assert_called_once()

    def test_get_sweeps_not_ok_response(self, fe):
        mock_resp = MagicMock(ok=False)

        with (
            patch.object(fe, "get_properties", return_value={"active_project": True, "project_list": ["p1"]}),
            patch("ansys.aedt.toolkits.radar_explorer.ui.actions.requests.get", return_value=mock_resp),
        ):
            result = fe.get_sweeps()

        assert result == ["Sweep"]
