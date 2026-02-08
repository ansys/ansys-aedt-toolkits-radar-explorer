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

from pathlib import Path  # noqa: I001

import pytest
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.toolkits.radar_explorer.backend.api import ToolkitBackend
from ansys.aedt.core.generic.file_utils import generate_unique_project_name

pytestmark = [pytest.mark.radar_toolkit_api]


@pytest.fixture()
def toolkit_api(desktop, common_temp_dir):
    version = desktop["version"]
    project = generate_unique_project_name(str(common_temp_dir))
    app = Hfss(version=version, project=project, new_desktop=False)
    design_name = app.design_name
    project_file = app.project_file
    non_graphical = desktop["non_graphical"]
    port = desktop["port"]
    app.release_desktop(False, False)

    toolkit_api = ToolkitBackend()
    toolkit_api.properties.active_design = design_name
    toolkit_api.properties.active_project = project_file
    toolkit_api.properties.non_graphical = non_graphical
    toolkit_api.properties.aedt_version = version
    project_name = toolkit_api.get_project_name(project_file)
    toolkit_api.properties.design_list = {project_name: [design_name]}
    toolkit_api.properties.selected_process = port
    toolkit_api.properties.active_design = design_name
    yield toolkit_api

    app = Hfss(version=version, port=port, new_desktop=False)
    app.close_project()


@pytest.fixture()
def toolkit_api_solved_project(desktop, common_temp_dir):
    version = desktop["version"]

    aedt_file_archived = Path(common_temp_dir) / "input_data" / "TriHedral_RCS.aedtz"
    # aedt_file = Path(common_temp_dir) / "input_data" / "trihedral.aedt"

    app = Hfss(version=version, project=aedt_file_archived, design="design_sbr_solved", new_desktop=False)
    design_name = app.design_name
    project_file = app.project_file
    non_graphical = desktop["non_graphical"]
    port = desktop["port"]
    app.release_desktop(False, False)

    toolkit_api = ToolkitBackend()
    toolkit_api.properties.active_design = design_name
    toolkit_api.properties.active_project = project_file
    toolkit_api.properties.non_graphical = non_graphical
    toolkit_api.properties.aedt_version = version
    project_name = toolkit_api.get_project_name(project_file)
    toolkit_api.properties.design_list = {project_name: [design_name]}
    toolkit_api.properties.selected_process = port
    toolkit_api.properties.active_design = design_name
    yield toolkit_api
    app = Hfss(version=version, port=port, new_desktop=False)
    app.close_project()


class TestClass:
    """Class defining a workflow to test rest api toolkit."""

    def test_update_rcs_properties(self):
        toolkit_api = ToolkitBackend()
        range_resolution = toolkit_api.properties.radar.range_res
        toolkit_api.properties.setup.fft_bandwidth = 11000000000.0
        toolkit_api.update_rcs_properties(range_is_system=True, azimuth_is_system=True, elevation_is_system=True)
        assert not range_resolution == toolkit_api.properties.radar.range_res
        toolkit_api.properties.radar.range_res_az = 50
        toolkit_api.properties.radar.range_res_el = 50
        toolkit_api.update_rcs_properties(range_is_system=False, azimuth_is_system=False, elevation_is_system=False)
        assert not range_resolution == toolkit_api.properties.radar.range_res

    def test_update_range_profile_properties(self):
        toolkit_api = ToolkitBackend()
        range_resolution = toolkit_api.properties.radar.range_res
        toolkit_api.properties.setup.fft_bandwidth = 10000000000.0
        toolkit_api.update_range_profile_properties(is_system=True)
        assert not range_resolution == toolkit_api.properties.radar.range_res
        toolkit_api.update_range_profile_properties(is_system=False)
        assert not range_resolution == toolkit_api.properties.radar.range_res

    def test_update_waterfall_properties(self):
        toolkit_api = ToolkitBackend()
        range_resolution = toolkit_api.properties.radar.range_res
        toolkit_api.properties.setup.fft_bandwidth = 11000000000.0
        toolkit_api.update_waterfall_properties(range_is_system=True, azimuth_is_system=True)
        assert not range_resolution == toolkit_api.properties.radar.range_res
        toolkit_api.update_waterfall_properties(range_is_system=False, azimuth_is_system=False)
        assert not range_resolution == toolkit_api.properties.radar.range_res

    def test_update_isar_2d_properties(self):
        toolkit_api = ToolkitBackend()
        range_resolution = toolkit_api.properties.radar.range_res
        toolkit_api.properties.setup.fft_bandwidth = 10000000000.0
        toolkit_api.update_isar_2d_properties(range_is_system=True, azimuth_is_system=True)
        assert not range_resolution == toolkit_api.properties.radar.range_res
        toolkit_api.update_isar_2d_properties(range_is_system=False, azimuth_is_system=False)
        assert not range_resolution == toolkit_api.properties.radar.range_res

    def test_is_sbr_design(self, toolkit_api):
        version = toolkit_api.properties.aedt_version
        port = toolkit_api.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        app.solution_type = "Modal"
        app.release_desktop(False, False)

        assert not toolkit_api.is_sbr_design()

        app = Hfss(version=version, port=port, new_desktop=False)
        app.solution_type = "SBR+"
        app.release_desktop(False, False)

        assert toolkit_api.is_sbr_design()

    def test_generate_3d_component(self, toolkit_api):
        version = toolkit_api.properties.aedt_version
        port = toolkit_api.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        app.solution_type = "Modal"
        app.modeler.create_box([0, 0, 0], [10, 10, 10], "box1", "copper")
        app.release_desktop(False, False)

        component = toolkit_api.generate_3d_component()
        assert component.is_file()

        # Call second time
        component = toolkit_api.generate_3d_component()
        assert component.is_file()
        assert toolkit_api.insert_sbr_design(str(component))
        assert toolkit_api.is_sbr_design()

        # Test with CS created by the toolkit
        toolkit_api.properties.setup.num_freq = 3
        toolkit_api.properties.setup.sim_freq_upper = 1.1e9
        toolkit_api.properties.radar.rotation_order = "ZXZ"
        assert toolkit_api.add_plane_wave(name="IncWaveVpol", polarization="Vertical")
        assert toolkit_api.add_setup(name="rcs_setup")

    def test_generate_3d_component_2(self, toolkit_api):
        version = toolkit_api.properties.aedt_version
        port = toolkit_api.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        app.solution_type = "Modal"
        box = app.modeler.create_box([0, 0, 0], [10, 10, 10], "box1", "copper")
        app.modeler.replace_3dcomponent(box.name)
        app.release_desktop(False, False)

        component = toolkit_api.generate_3d_component()
        assert component.is_file()

    def test_duplicate_design(self, toolkit_api):
        version = toolkit_api.properties.aedt_version
        port = toolkit_api.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        app.solution_type = "Modal"
        box = app.modeler.create_box([0, 0, 0], [10, 10, 10], "box1", "copper")
        app.modeler.replace_3dcomponent(box.name)
        app.modeler.create_box([0, 0, 0], [10, 10, 10], "box2", "copper")
        app.release_desktop(False, False)
        assert toolkit_api.duplicate_sbr_design("duplicated_design")
        project_name = toolkit_api.get_project_name(toolkit_api.properties.active_project)
        assert "duplicated_design" in toolkit_api.properties.design_list[project_name]

    def test_add_plane_wave(self, toolkit_api):
        version = toolkit_api.properties.aedt_version
        port = toolkit_api.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        app.solution_type = "SBR+"
        app.release_desktop(False, False)
        toolkit_api.properties.radar.calculation_type = "RCS"
        toolkit_api.properties.radar.num_phi = 3
        toolkit_api.properties.radar.num_theta = 3
        assert toolkit_api.add_plane_wave(name="IncWaveVpol", polarization="Vertical")
        assert toolkit_api.add_plane_wave(name="IncWaveHpol", polarization="Horizontal")

    def test_add_setup(self, toolkit_api):
        version = toolkit_api.properties.aedt_version
        port = toolkit_api.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        app.modeler.create_coordinate_system(mode="zyz")
        app.solution_type = "SBR+"
        app.save_project()
        app.release_desktop(False, False)
        toolkit_api.properties.setup.num_freq = 3
        toolkit_api.properties.setup.sim_freq_upper = 1.1e9
        toolkit_api.properties.setup.ptd_utd = True
        toolkit_api.properties.radar.rotation_order = "ZYZ"
        toolkit_api.add_plane_wave(name="IncWaveHpol", polarization="Horizontal")
        assert toolkit_api.add_setup()

    def test_export_rcs(self, toolkit_api_solved_project):
        version = toolkit_api_solved_project.properties.aedt_version
        port = toolkit_api_solved_project.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        excitations = app.excitation_names
        app.release_desktop(False, False)

        toolkit_api_solved_project.properties.setup.setup_name = "SBR"

        encoded_data = toolkit_api_solved_project.export_rcs(encode=True)
        assert len(encoded_data) == 3

        assert toolkit_api_solved_project.export_rcs(encode=False)

        encoded_data = toolkit_api_solved_project.export_rcs(encode=True, excitation=excitations[0])
        assert len(encoded_data) == 3

        metadata_file = toolkit_api_solved_project.export_rcs(encode=False, excitation=excitations[1])
        assert Path(metadata_file).is_file()

        # Sometimes solution is invalidated
        toolkit_api_solved_project.properties.setup.solve_interactive = True
        toolkit_api_solved_project.analyze()
        metadata_file = toolkit_api_solved_project.export_rcs("IncWaveVpol", "ComplexMonostaticRCSTheta", encode=False)
        assert Path(metadata_file).is_file()

        encoded_data = toolkit_api_solved_project.export_rcs("IncWaveVpol", "ComplexMonostaticRCSTheta", encode=True)
        assert len(encoded_data) == 3

        encoded_data = toolkit_api_solved_project.export_rcs("IncWaveVpol", "ComplexMonostaticRCSPhi", encode=True)
        assert len(encoded_data) == 3

        setups = toolkit_api_solved_project.get_setups()
        assert len(setups) == 1

        setups = toolkit_api_solved_project.get_setups()
        assert len(setups) == 1

        plane_waves = toolkit_api_solved_project.get_plane_waves()
        assert len(plane_waves) == 2

    def test_import_cad(self, toolkit_api, common_temp_dir):
        version = toolkit_api.properties.aedt_version
        port = toolkit_api.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        app.solution_type = "SBR+"
        app.release_desktop(False, False)

        toolkit_api.properties.cad.material = ["invented"]
        assert not toolkit_api.insert_cad_sbr()

        car = Path(common_temp_dir) / "input_data" / "geometries" / "car_stl.stl"
        rv = Path(common_temp_dir) / "input_data" / "geometries" / "rv.glb"
        rv2 = Path(common_temp_dir) / "input_data" / "geometries" / "rv1.obj"

        toolkit_api.properties.cad.input_file = [car, rv, rv2]
        toolkit_api.properties.cad.material = ["pec"]
        assert not toolkit_api.insert_cad_sbr()

        toolkit_api.properties.cad.material = None
        toolkit_api.properties.cad.position = None
        assert toolkit_api.insert_cad_sbr()
        toolkit_api.properties.cad.position = [[0, 0, 0]]
        assert not toolkit_api.insert_cad_sbr()

    def test_import_cad_finite_conductivity(self, toolkit_api, common_temp_dir):
        version = toolkit_api.properties.aedt_version
        port = toolkit_api.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        app.solution_type = "SBR+"
        app.release_desktop(False, False)

        car = Path(common_temp_dir) / "input_data" / "geometries" / "car_stl.stl"

        toolkit_api.properties.cad.input_file = [car]
        toolkit_api.properties.cad.material = ["aluminum"]
        assert toolkit_api.insert_cad_sbr()

    def test_available_materials(self, toolkit_api):
        version = toolkit_api.properties.aedt_version
        port = toolkit_api.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        app.solution_type = "SBR+"
        app.release_desktop(False, False)

        materials = toolkit_api.get_materials()
        assert materials

    def test_available_sweeps(self, toolkit_api):
        version = toolkit_api.properties.aedt_version
        port = toolkit_api.properties.selected_process
        app = Hfss(version=version, port=port, new_desktop=False)
        app.solution_type = "Modal"
        setup = app.create_setup("Setup1")
        toolkit_api.properties.setup.setup_name = setup.name
        sweep = app.create_linear_count_sweep(setup.name, "GHz", 1e9, 2e9, 11)
        app.save_project()
        app.release_desktop(False, False)

        sweep_list = toolkit_api.get_sweeps()
        assert sweep.name in sweep_list
