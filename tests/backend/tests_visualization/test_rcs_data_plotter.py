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

import json
from pathlib import Path
import shutil
import warnings

import pandas as pd
import pytest

from ansys.aedt.core.internal.checks import ERROR_GRAPHICS_REQUIRED
from ansys.aedt.core.internal.checks import check_graphics_available
from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSData
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter
from tests import TESTS_VISUALIZATION_PATH

try:
    check_graphics_available()

    from ansys.tools.visualization_interface import Plotter
except ImportError:  # pragma: no cover
    warnings.warn(ERROR_GRAPHICS_REQUIRED)


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class."""
    return


@pytest.fixture(scope="class")
def setup_test_data(request, local_scratch):
    """Fixture to set up the test data directory and file before running the test class."""
    dir_original = Path(TESTS_VISUALIZATION_PATH) / "example_models"
    data_dir = Path(local_scratch.path) / "rcs_files"
    shutil.copytree(dir_original, data_dir)

    metadata = {
        "solution": "Trihedral_RCS",
        "monostatic_file": "rcs_data.h5",
        "model_units": "mm",
        "frequency_units": "GHz",
        "model_info": {
            "Polyline1": ["Polyline1.obj", [143, 175, 143], 1.0, "mm"],
            "Polyline1_1": ["Polyline1_1.obj", [143, 0, 0], 1.0, "mm"],
            "Polyline1_2": ["Polyline1_2.obj", [255, 255, 0], 1.0, "mm"],
        },
    }
    metadata_file = data_dir / "rcs_metadata.json"
    with metadata_file.open("w") as f:
        json.dump(metadata, f)
    request.cls.metadata_file = metadata_file

    metadata_fake = {
        "solution": "Trihedral_RCS",
        "monostatic_file": "invented.h5",
        "model_units": "mm",
        "frequency_units": "GHz",
        "model_info": {
            "Polyline1": ["Polyline1.obj", [143, 175, 143], 1.0, "mm"],
            "Polyline1_1": ["Polyline1_1.obj", [143, 175, 143], 1.0, "mm"],
            "Polyline1_2": ["Polyline1_2.obj", [143, 175, 143], 1.0, "mm"],
        },
    }
    metadata_file_fake = data_dir / "rcs_metadata_fake.json"
    with metadata_file_fake.open("w") as f:
        json.dump(metadata_fake, f)
    request.cls.metadata_file_fake = metadata_file_fake

    metadata_no_data = {
        "solution": "Trihedral_RCS",
        "monostatic_file": None,
        "model_units": "mm",
        "frequency_units": None,
        "model_info": {
            "Polyline1": ["Polyline1.obj", [143, 175, 143], 1.0, "mm"],
            "Polyline1_1": ["Polyline1_1.obj", [143, 175, 143], 1.0, "mm"],
            "Polyline1_2": ["Polyline1_2.obj", [143, 175, 143], 1.0, "mm"],
        },
    }
    metadata_file_no_data = data_dir / "rcs_metadata_no_data.json"
    with metadata_file_no_data.open("w") as f:
        json.dump(metadata_no_data, f)
    request.cls.metadata_file_no_data = metadata_file_no_data
    yield


@pytest.mark.usefixtures("setup_test_data")
class TestClass:
    def test_rcs_data(self):
        with pytest.raises(Exception, match="JSON file does not exist."):
            MonostaticRCSData(input_file="invented")

        with pytest.raises(Exception, match="Monostatic file is invalid."):
            MonostaticRCSData(input_file=str(self.metadata_file_fake))

        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        assert isinstance(rcs_data.raw_data, pd.DataFrame)

        assert isinstance(rcs_data.metadata, dict)

        assert rcs_data.name == "HH"
        assert rcs_data.solution == "Trihedral_RCS"
        assert Path(rcs_data.input_file).is_file()
        assert rcs_data.frequency_units == "GHz"
        assert len(rcs_data.frequencies) == 3

        assert rcs_data.available_incident_wave_theta.size == 3
        assert rcs_data.incident_wave_theta == rcs_data.available_incident_wave_theta[0]

        rcs_data.incident_wave_theta = 89.0
        assert rcs_data.incident_wave_theta == rcs_data.available_incident_wave_theta[0]

        rcs_data.incident_wave_theta = rcs_data.available_incident_wave_theta[1]
        assert rcs_data.incident_wave_theta == rcs_data.available_incident_wave_theta[1]

        rcs_data.incident_wave_theta = 80.0
        assert rcs_data.incident_wave_theta == rcs_data.available_incident_wave_theta[1]

        rcs_data.incident_wave_phi = -40.0
        assert rcs_data.incident_wave_phi == rcs_data.available_incident_wave_phi[0]

        rcs_data.incident_wave_phi = -1e9
        assert rcs_data.incident_wave_phi == rcs_data.available_incident_wave_phi[0]

        assert rcs_data.frequency == rcs_data.frequencies[0]

        rcs_data.frequency = f"{rcs_data.frequencies[1]}GHz"
        assert rcs_data.frequency == rcs_data.frequencies[1]

        rcs_data.frequency = rcs_data.frequencies[2]
        assert rcs_data.frequency == rcs_data.frequencies[2]

        rcs_data.frequency = 8.0
        assert rcs_data.frequency == rcs_data.frequencies[2]

        assert rcs_data.data_conversion_function == "dB20"
        rcs_data.data_conversion_function = "abs"
        assert rcs_data.data_conversion_function == "abs"

        assert rcs_data.window == "Flat"

        rcs_data.window = "Hamming"
        assert rcs_data.window == "Hamming"

        rcs_data.window = "Hann"
        assert rcs_data.window == "Hann"

        rcs_data.window = "invented"
        assert rcs_data.window == "Hann"

        assert rcs_data.window_size == 1024
        rcs_data.window_size = 512
        assert rcs_data.window_size == 512

        assert rcs_data.aspect_range == "Horizontal"
        rcs_data.aspect_range = "Vertical"
        assert rcs_data.aspect_range == "Vertical"

        assert rcs_data.upsample_range == 512
        rcs_data.upsample_range = 24
        assert rcs_data.upsample_range == 24

        assert rcs_data.upsample_azimuth == 64
        rcs_data.upsample_azimuth = 32
        assert rcs_data.upsample_azimuth == 32

        assert rcs_data.interpolation == "linear"
        rcs_data.interpolation = "nearest"
        assert rcs_data.interpolation == "nearest"
        rcs_data.interpolation = "invented"
        assert rcs_data.interpolation == "nearest"

        assert rcs_data.extrapolate
        rcs_data.extrapolate = False
        assert not rcs_data.extrapolate
        rcs_data.extrapolate = 1
        assert not rcs_data.extrapolate

        assert rcs_data.gridsize == "Middle"
        rcs_data.gridsize = "Outside"
        assert rcs_data.gridsize == "Outside"
        rcs_data.gridsize = "invented"
        assert rcs_data.gridsize == "Outside"

        assert rcs_data.upsample_elevation == 64
        rcs_data.upsample_elevation = 2
        assert rcs_data.upsample_elevation == 2

        assert isinstance(rcs_data.rcs, complex)

        assert isinstance(rcs_data.rcs_active_theta_phi, pd.DataFrame)
        assert isinstance(rcs_data.rcs_active_frequency, pd.DataFrame)
        assert isinstance(rcs_data.rcs_active_theta, pd.DataFrame)
        assert isinstance(rcs_data.rcs_active_phi, pd.DataFrame)

        assert isinstance(rcs_data.range_profile, pd.DataFrame)
        assert isinstance(rcs_data.waterfall, pd.DataFrame)

        assert isinstance(rcs_data.isar_2d, pd.DataFrame)
        rcs_data.aspect_range = "Horizontal"
        assert isinstance(rcs_data.isar_2d, pd.DataFrame)
        rcs_data.gridsize = "Inside"
        assert isinstance(rcs_data.isar_2d, pd.DataFrame)

        rcs_data.upsample_range = 2
        assert isinstance(rcs_data.isar_2d, pd.DataFrame)

        rcs_data.gridsize = "Inside"
        assert isinstance(rcs_data.isar_3d, pd.DataFrame)
        rcs_data.gridsize = "Outside"
        assert isinstance(rcs_data.isar_3d, pd.DataFrame)
        rcs_data.gridsize = "Middle"
        assert isinstance(rcs_data.isar_3d, pd.DataFrame)

        rcs_data.upsample_range = 0
        rcs_data.upsample_azimuth = 0
        rcs_data.upsample_elevation = 0
        assert isinstance(rcs_data.isar_3d, pd.DataFrame)

        assert rcs_data.window_function("Hann")
        assert rcs_data.window_function("Hamming")
        assert rcs_data.window_function()

    def test_rcs_plotter_properties(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        assert rcs_plotter.rcs_data

        assert isinstance(rcs_plotter.model_info, dict)
        assert rcs_plotter.model_units == "mm"
        assert isinstance(rcs_plotter.all_scene_actors, dict)
        assert len(rcs_plotter.extents) == 6
        assert rcs_plotter.center.size == 3
        assert isinstance(rcs_plotter.radius, float)

        assert rcs_plotter.num_contours == 10
        rcs_plotter.num_contours = 2
        assert rcs_plotter.num_contours == 2

    def test_rcs_plotter_rcs(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter1 = rcs_plotter.plot_rcs(
            show=False, primary_sweep="Freq", secondary_sweep="IWaveTheta", is_polar=True
        )
        assert isinstance(rcs_plotter1, ReportPlotter)

        rcs_plotter2 = rcs_plotter.plot_rcs(show=False, primary_sweep="Freq", secondary_sweep="IWavePhi")
        assert isinstance(rcs_plotter2, ReportPlotter)

        rcs_plotter3 = rcs_plotter.plot_rcs(show=False, primary_sweep="IWavePhi", secondary_sweep_value="all")
        assert isinstance(rcs_plotter3, ReportPlotter)

        rcs_plotter4 = rcs_plotter.plot_rcs(show=False, primary_sweep="IWavePhi", secondary_sweep_value=None)
        assert isinstance(rcs_plotter4, ReportPlotter)

        rcs_plotter5 = rcs_plotter.plot_rcs(show=False, primary_sweep="IWaveTheta", secondary_sweep_value="all")
        assert isinstance(rcs_plotter5, ReportPlotter)

        rcs_plotter6 = rcs_plotter.plot_rcs(show=False, primary_sweep="IWaveTheta", secondary_sweep_value=None)
        assert isinstance(rcs_plotter6, ReportPlotter)

        rcs_plotter7 = rcs_plotter.plot_rcs_3d(show=False)
        assert isinstance(rcs_plotter7, ReportPlotter)

    def test_rcs_plotter_range_profile(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter = rcs_plotter.plot_range_profile(show=False)
        assert isinstance(rcs_plotter, ReportPlotter)

    def test_rcs_plotter_waterfall(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter1 = rcs_plotter.plot_waterfall(show=False)
        assert isinstance(rcs_plotter1, ReportPlotter)

        rcs_plotter2 = rcs_plotter.plot_waterfall(show=False, is_polar=True)
        assert isinstance(rcs_plotter2, ReportPlotter)

        rcs_plotter.rcs_data.aspect_range = "Vertical"
        rcs_plotter3 = rcs_plotter.plot_waterfall(show=False, is_polar=True)
        assert isinstance(rcs_plotter3, ReportPlotter)

    def test_rcs_plotter_2d_isar(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter1 = rcs_plotter.plot_isar_2d(show=False)
        assert isinstance(rcs_plotter1, ReportPlotter)

    def test_rcs_plotter_3d_isar(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter1 = rcs_plotter.plot_isar_3d(show=False)
        assert isinstance(rcs_plotter1, ReportPlotter)

        with pytest.raises(ValueError):
            rcs_plotter.plot_isar_3d(show=False, plane_cut=None)

        with pytest.raises(ValueError):
            rcs_plotter.plot_isar_3d(show=False, plane_cut="xy", plane_offset=None)

        rcs_plotter2 = rcs_plotter.plot_isar_3d(show=False, plane_cut="XY")
        assert isinstance(rcs_plotter2, ReportPlotter)

        rcs_plotter2 = rcs_plotter.plot_isar_3d(show=False, plane_cut="yz")
        assert isinstance(rcs_plotter2, ReportPlotter)

        with pytest.raises(ValueError):
            rcs_plotter.plot_isar_3d(show=False, plane_cut="invented")

    def test_rcs_plotter_add_rcs(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter.add_rcs()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_rcs(color_bar="green")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        assert not rcs_plotter.clear_scene(first_level="model")
        assert rcs_plotter.clear_scene(first_level="results")
        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_add_range_profile(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter.add_range_profile()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_range_profile(plot_type="invented", color_bar="red")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_range_profile(plot_type="projection")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_range_profile(plot_type="plane v")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_range_profile(plot_type="plane h")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_range_profile(plot_type="extruded")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_range_profile(plot_type="rotated")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_add_waterfall(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter.add_waterfall()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.rcs_data.aspect_range = "Vertical"
        rcs_plotter.add_waterfall()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        assert rcs_plotter.clear_scene()

        with pytest.raises(ValueError):
            rcs_plotter.rcs_data.aspect_range = "invented"
            rcs_plotter.add_waterfall()

    def test_rcs_plotter_add_isar_2d(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)
        rcs_plotter.show_geometry = False

        rcs_plotter.add_isar_2d()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.rcs_data.aspect_range = "Vertical"
        rcs_plotter.add_isar_2d("Relief")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        assert rcs_plotter.clear_scene()

        rcs_plotter.add_isar_2d("Projection")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        with pytest.raises(ValueError):
            rcs_plotter.rcs_data.aspect_range = "invented"
            rcs_plotter.add_isar_2d("Projection")

    def test_rcs_plotter_add_isar_3d(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)
        rcs_plotter.show_geometry = False

        rcs_plotter.add_isar_3d()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_isar_3d(plot_type="point cloud")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_isar_3d(plot_type="plane cut", plane_cut="xy", plane_offset=0)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_isar_3d(plot_type="plane cut", plane_cut="xz", plane_offset=0)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_isar_3d(plot_type="plane cut", plane_cut="yz", plane_offset=0)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        rcs_plotter.add_isar_3d(plot_type="projection", plane_cut="yz", plane_offset=0)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

        assert rcs_plotter.clear_scene()

        with pytest.raises(ValueError):
            rcs_plotter.add_isar_3d(plot_type="plane cut", plane_cut=None)

        with pytest.raises(ValueError):
            rcs_plotter.add_isar_3d(plot_type="plane cut", plane_offset=None)

        with pytest.raises(ValueError):
            rcs_plotter.add_isar_3d(plot_type="plane cut", plane_cut="invented", plane_offset=0)

        with pytest.raises(ValueError):
            rcs_plotter.add_isar_3d(plot_type="plane cut", plane_cut="invented", plane_offset=None)

    def test_rcs_plotter_add_profile_settings(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter.add_range_profile_settings()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_add_waterfall_settings(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter.add_waterfall_settings(aspect_ang_phi=250.0)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter = MonostaticRCSPlotter()

        rcs_plotter.add_waterfall_settings(aspect_ang_phi=90.0)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_add_isar_2d_settings(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter.add_isar_2d_settings(
            size_range=0.5, range_resolution=0.01, size_cross_range=0.6, cross_range_resolution=0.02
        )
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_add_isar_3d_settings(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)

        rcs_plotter.add_isar_3d_settings(
            size_range=1.0,
            range_resolution=0.01,
            size_cross_range=1.0,
            cross_range_resolution=0.01,
            size_elevation_range=1.0,
            elevation_range_resolution=0.01,
        )
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_no_data(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file_no_data))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)
        rcs_plotter.show_geometry = False

        rcs_plotter.add_range_profile_settings()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_only_settings(self):
        rcs_plotter = MonostaticRCSPlotter()
        rcs_plotter.add_range_profile_settings()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)

    def test_rcs_plotter_add_incident_rcs_settings(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)
        rcs_plotter.add_incident_rcs_settings(theta_span=20, num_theta=101, phi_span=20, num_phi=101)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter.add_incident_rcs_settings(theta_span=20, num_theta=101, phi_span=20, num_phi=101, line_color="blue")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter.add_incident_rcs_settings(
            theta_span=20, num_theta=101, phi_span=20, num_phi=101, arrow_color="black"
        )
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter.add_incident_rcs_settings(
            theta_span=20, num_theta=101, phi_span=20, num_phi=101, arrow_color="pink"
        )
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter = MonostaticRCSPlotter()
        rcs_plotter.add_incident_rcs_settings(theta_span=20, num_theta=101, phi_span=20, num_phi=101)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_add_incident_range_profile_settings(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)
        rcs_plotter.add_incident_range_profile_settings()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter = MonostaticRCSPlotter()
        rcs_plotter.add_incident_range_profile_settings()
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_add_incident_isar3d_settings(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)
        rcs_plotter.add_incident_isar_3d_settings(theta_span=20, num_theta=101, phi_span=20, num_phi=101)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter.add_incident_isar_3d_settings(
            theta_span=20, num_theta=101, phi_span=20, num_phi=101, line_color="blue"
        )
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter.add_incident_isar_3d_settings(
            theta_span=20, num_theta=101, phi_span=20, num_phi=101, arrow_color="black"
        )
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter = MonostaticRCSPlotter()
        rcs_plotter.add_incident_isar_3d_settings(theta_span=20, num_theta=101, phi_span=20, num_phi=101)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_add_incident_isar2d_settings(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)
        rcs_plotter.add_incident_isar_2d_settings(phi_span=20, num_phi=101)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter.add_incident_isar_2d_settings(phi_span=20, num_phi=101, line_color="blue")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter = MonostaticRCSPlotter()
        rcs_plotter.add_incident_isar_2d_settings(phi_span=20, num_phi=101)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

    def test_rcs_plotter_add_incident_waterfall_settings(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)
        rcs_plotter.add_incident_waterfall_settings(phi_span=20, num_phi=101)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter.add_incident_waterfall_settings(phi_span=20, num_phi=101, line_color="blue")
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

        rcs_plotter = MonostaticRCSPlotter()
        rcs_plotter.add_incident_waterfall_settings(phi_span=20, num_phi=101)
        plot = rcs_plotter.plot_scene(show=False)
        assert isinstance(plot, Plotter)
        assert rcs_plotter.clear_scene()

    def test_scene_mesh_object(self):
        rcs_data = MonostaticRCSData(input_file=str(self.metadata_file))
        rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_data)
        rcs_plotter.show_geometry = False

        rcs_plotter.add_isar_2d()
        isar_object = rcs_plotter.all_scene_actors["results"]["isar_2d"]["isar_2d_0"]

        assert isar_object.custom_object.z_offset == 0.0
        isar_object.custom_object.z_offset = 1.0
        assert isar_object.custom_object.z_offset == 1.0

        assert isar_object.custom_object.scale_factor
        isar_object.custom_object.scale_factor = 2.0
        assert isar_object.custom_object.scale_factor == 2.0

        assert isar_object.custom_object.default_clim
        isar_object.custom_object.default_clim = (0.0, 1.0)
        assert isar_object.custom_object.default_clim == (0.0, 1.0)

        assert isar_object.custom_object.default_mesh

        assert isar_object.custom_object.plot_type
        isar_object.custom_object.plot_type = "projection"
        assert isar_object.custom_object.plot_type == "projection"

        isar_object.custom_object.reset_scene()

        assert isar_object.custom_object.name
        assert isar_object.custom_object.line_width
        assert isar_object.custom_object.opacity
        assert not isar_object.custom_object.color
        assert isar_object.custom_object.scalar_dict
