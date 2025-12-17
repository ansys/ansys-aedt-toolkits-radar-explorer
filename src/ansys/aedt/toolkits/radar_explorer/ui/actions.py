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

import base64
from pathlib import Path
import tempfile

from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSData
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter

# isort: off

from ansys.aedt.toolkits.common.ui.logger_handler import logger
from ansys.aedt.toolkits.common.ui.actions_generic import FrontendGeneric

# isort: on

import requests

"""Default timeout for requests in seconds."""
DEFAULT_REQUESTS_TIMEOUT = 120


class Frontend(FrontendGeneric):
    def __init__(self):
        FrontendGeneric.__init__(self)
        self.temp_folder = tempfile.mkdtemp()

    @staticmethod
    def load_rcs_data_from_file(input_file=None) -> MonostaticRCSPlotter | bool:
        if not input_file:
            return MonostaticRCSPlotter()
        if not Path(input_file).exists():
            logger.error("File does not exist")
            return False
        rcs_data = MonostaticRCSData(input_file=input_file)
        return MonostaticRCSPlotter(rcs_data=rcs_data)

    def get_setups(self):
        """Get a list of available setups.

        Returns
        -------
        list
            List of setups. Returns ["No Setup"] if no projects are available.
        """
        be_properties = self.get_properties()
        setup_list = []
        if be_properties["active_project"]:
            if be_properties["project_list"]:
                response = requests.get(self.url + "/get_setups", timeout=DEFAULT_REQUESTS_TIMEOUT)
                if response.ok:
                    setups = response.json()
                    setup_list = list(setups)
        if not setup_list:
            setup_list.append("No Setup")
        return setup_list

    def get_plane_waves(self):
        """Get a list of available plane waves.

        Returns
        -------
        list
            List of plane waves. Returns ["No Setup"] if no projects are available.
        """
        be_properties = self.get_properties()
        setup_list = []
        if be_properties["active_project"]:
            if be_properties["project_list"]:
                response = requests.get(self.url + "/get_plane_waves", timeout=DEFAULT_REQUESTS_TIMEOUT)
                if response.ok:
                    setups = response.json()
                    setup_list = list(setups)
        if not setup_list:
            setup_list.append("No Setup")
        return setup_list

    def get_materials(self):
        """Get a list of available materials.

        Returns
        -------
        list
           List of available materials.
        """
        be_properties = self.get_properties()
        materials_list = []
        if be_properties["active_project"]:
            if be_properties["project_list"]:
                response = requests.get(self.url + "/get_materials", timeout=DEFAULT_REQUESTS_TIMEOUT)
                if response.ok:
                    materials = response.json()
                    materials_list = list(materials)
        if not materials_list:
            materials_list.append("pec")
        return materials_list

    def get_sweeps(self):
        """Get a list of available sweeps.

        Returns
        -------
        list
           List of available sweeps.
        """
        be_properties = self.get_properties()
        sweep_list = ["Sweep"]
        if be_properties["active_project"]:
            if be_properties["project_list"]:
                response = requests.get(self.url + "/get_sweeps", timeout=DEFAULT_REQUESTS_TIMEOUT)
                if response.ok:
                    sweeps = response.json()
                    sweep_list = list(sweeps)
        return sweep_list

    def export_rcs(self, excitation=None, expression=None):
        """Get RCS data."""
        rcs_metadata = None
        values = {
            "excitation": excitation,
            "expression": expression,
            "encode": True,
        }

        if self.properties.backend_url in ["127.0.0.1", "localhost"]:
            values["encode"] = False
            response = requests.get(self.url + "/export_rcs", json=values)  # nosec B113
            if response.ok:
                rcs_metadata = response.json()
        else:
            response = requests.get(self.url + "/export_rcs", json=values)  # nosec B113
            if response.ok:
                data = response.json()

                # Create directories
                Path(self.temp_folder).mkdir()
                (Path(self.temp_folder) / "geometry").mkdir()

                # Metadata file
                encoded_data_bytes = bytes(data[0], "utf-8")
                decoded_data = base64.b64decode(encoded_data_bytes)
                rcs_metadata = Path(self.temp_folder) / "pyaedt_rcs_metadata.json"
                with rcs_metadata.open("wb") as f:
                    f.write(decoded_data)

                metadata = read_json(rcs_metadata)

                # Geometry files
                cont_geom = 0
                for encoded_data in data[1]:
                    geometry_names = list(metadata["model_info"].keys())
                    encoded_data_bytes = bytes(encoded_data, "utf-8")
                    decoded_data = base64.b64decode(encoded_data_bytes)
                    file_path = Path(self.temp_folder) / "geometry" / str(geometry_names[cont_geom] + ".obj")
                    with file_path.open("wb") as f:
                        f.write(decoded_data)
                    cont_geom += 1

                # RCS files
                if excitation or expression:
                    encoded_data_bytes = bytes(data[2], "utf-8")
                    decoded_data = base64.b64decode(encoded_data_bytes)
                    rcs_data = Path(self.temp_folder) / metadata["monostatic_file"]
                    with rcs_data.open("wb") as f:
                        f.write(decoded_data)

        if rcs_metadata:
            metadata = read_json(rcs_metadata)
            if metadata["monostatic_file"] is None:
                msg = "Geometry was extracted."
            else:
                monostatic_file = metadata["monostatic_file"]
                msg = f"Geometry and radar results were extracted from {monostatic_file}."
            self.ui.update_logger(msg)
            logger.debug(msg)
            return rcs_metadata

        else:
            msg = "RCS was not extracted"
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    def release_desktop(self, close_projects=True, close_on_exit=True):
        """Release AEDT."""
        properties = {"close_projects": close_projects, "close_on_exit": close_on_exit}
        requests.post(self.url + "/close_aedt", json=properties, timeout=DEFAULT_REQUESTS_TIMEOUT)
        return True

    def generate_3d_component(self):
        """Generate a 3D component."""
        response = requests.get(self.url + "/generate_3d_component")  # nosec B113

        if response.ok:
            component_file = response.json()
            msg = "3D component was generated."
            self.ui.update_logger(msg)
            logger.debug(msg)
            return component_file
        else:
            msg = "3D component generation failed."
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    def insert_sbr_design(self, component_file, design_name="RCS_Design"):
        """Insert an SBR design."""
        values = {
            "input_file": component_file,
            "name": design_name,
        }
        response = requests.get(self.url + "/insert_sbr_design", json=values)  # nosec B113

        if response.ok:
            msg = "Component inserted in new design."
            self.ui.update_logger(msg)
            logger.debug(msg)
            return True
        else:
            msg = "Component not inserted in new design."
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    def insert_cad_design(self, input_file, material="pec", position=None, units="meter"):
        """Insert CAD."""
        if not position:
            position = ["0.0m"] * 3

        values = {
            "input_file": input_file,
            "material": material,
            "position": position,
            "extension": input_file.suffix,
            "units": units,
        }

        if self.properties.backend_url in ["127.0.0.1", "localhost"]:
            values["input_file"] = str(input_file)
            response = requests.put(self.url + "/insert_cad", json=values)  # nosec B113
        else:
            # Encode file
            serialized_file = self.serialize_obj_base64(input_file)
            decoded_file = serialized_file.decode("utf-8")
            values["input_file"] = decoded_file
            response = requests.put(self.url + "/insert_cad", json=values)  # nosec B113

        if response.ok:
            msg = "Component inserted in new design."
            self.ui.update_logger(msg)
            logger.debug(msg)
            return True
        else:
            msg = "Component not inserted in new design."
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    def rcs_setup(self):
        """Get a list of available plane waves.

        Returns
        -------
        list
            List of plane waves. Returns ["No Setup"] if no projects are available.
        """
        be_properties = self.get_properties()

        max_range = Quantity(self.mode_select_menu.max_range_textbox.text())
        be_properties["radar"]["range_max"] = max_range.value

        range_res = Quantity(self.mode_select_menu.range_res_textbox.text())
        be_properties["radar"]["range_res"] = range_res.value

        mode = self.mode_select_menu.mode_selection_combobox.currentText()
        be_properties["radar"]["calculation_type"] = mode

        # Azimuth
        aspect_angle_phi = Quantity(self.mode_select_menu.aspect_angle_phi_textbox.text())
        be_properties["radar"]["aspect_ang_phi"] = aspect_angle_phi.value  # this name must be the same
        # as ToolkitBackend.properties.radar

        be_properties["radar"]["num_phi"] = int(self.mode_select_menu.num_inc_phi_textbox.text())

        range_max_az = Quantity(self.mode_select_menu.max_cross_range_az_textbox.text())
        be_properties["radar"]["range_max_az"] = range_max_az.value

        range_res_az = Quantity(self.mode_select_menu.cross_range_az_res_textbox.text())
        be_properties["radar"]["range_res_az"] = range_res_az.value

        # Elevation
        aspect_angle_theta = Quantity(self.mode_select_menu.aspect_angle_theta_textbox.text())
        be_properties["radar"]["aspect_ang_theta"] = aspect_angle_theta.value

        be_properties["radar"]["num_theta"] = int(self.mode_select_menu.num_inc_theta_textbox.text())

        range_max_el = Quantity(self.mode_select_menu.max_cross_range_el_textbox.text())
        be_properties["radar"]["range_max_el"] = range_max_el.value

        range_res_el = Quantity(self.mode_select_menu.cross_range_el_res_textbox.text())
        be_properties["radar"]["range_res_el"] = range_res_el.value

        new_props = self.set_properties(be_properties)

        if not new_props:
            return False

        # Setup properties

        be_properties["setup"]["ffl"] = self.solver_setup_menu.toggle.isChecked()
        be_properties["setup"]["ray_density"] = Quantity(self.solver_setup_menu.ray_density_textbox.text()).value
        be_properties["setup"]["num_bounces"] = int(self.solver_setup_menu.num_bounces_textbox.text())
        be_properties["setup"]["ptd_utd"] = self.solver_setup_menu.ptd_utd.isChecked()
        be_properties["setup"]["solve_interactive"] = self.solver_setup_menu.solve_interactive.isChecked()
        be_properties["setup"]["num_cores"] = int(self.solver_setup_menu.cores_textbox.text())

        center_freq = Quantity(self.mode_select_menu.center_freq_textbox.text())
        be_properties["setup"]["center_freq"] = center_freq.to("Hz").value

        # Range
        fft_bandwidth = Quantity(self.mode_select_menu.fft_bandwidth_textbox.text())
        be_properties["setup"]["fft_bandwidth"] = fft_bandwidth.to("Hz").value
        be_properties["setup"]["sim_freq_lower"] = self.mode_select_menu.sim_freq_lower
        be_properties["setup"]["sim_freq_upper"] = self.mode_select_menu.sim_freq_upper

        be_properties["setup"]["num_freq"] = int(self.mode_select_menu.num_freq_textbox.text())

        _ = self.set_properties(be_properties)

        # Incident wave

        angle1 = Quantity(self.incident_wave_menu.angle1_textbox.text())
        be_properties["radar"]["rotation_ang1"] = angle1.value

        angle2 = Quantity(self.incident_wave_menu.angle2_textbox.text())
        be_properties["radar"]["rotation_ang2"] = angle2.value

        angle3 = Quantity(self.incident_wave_menu.angle3_textbox.text())
        be_properties["radar"]["rotation_ang3"] = angle3.value

        be_properties["radar"]["rotation_order"] = self.incident_wave_menu.rotation_combobox.currentText()

        new_props = self.set_properties(be_properties)

        if new_props:
            response = requests.get(self.url + "/add_plane_wave", timeout=DEFAULT_REQUESTS_TIMEOUT)

            if response.ok:
                _ = response.json()
                msg = "Plane waves were created."
                self.ui.update_logger(msg)
                logger.debug(msg)

                response = requests.get(self.url + "/create_setup", timeout=DEFAULT_REQUESTS_TIMEOUT)
                if response.ok:
                    _ = response.json()
                    msg = "Setup was created."
                    self.ui.update_logger(msg)
                    logger.debug(msg)
                else:
                    msg = "Setup creation failed."
                    self.ui.update_logger(msg)
                    logger.error(msg)
                    return False

            else:
                msg = "Plane waves creation failed."
                self.ui.update_logger(msg)
                logger.error(msg)
                return False
        return True

    def analyze(self):
        msg = "Starting analysis..."
        self.ui.update_logger(msg)

        response = requests.post(self.url + "/analyze")  # nosec B113

        if response.ok:
            msg = "Simulation was solved."
            self.ui.update_logger(msg)
            logger.debug(msg)
            return True

        else:
            msg = response.json()
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    @staticmethod
    def serialize_obj_base64(file_path):
        """Encode a bytes-like object.

        Parameters
        ----------
        file_path : str
            Path to the file to serialize.

        Returns
        -------
        bytes
            Encoded data.
        """
        with Path(file_path).open("rb") as f:
            data = f.read()
        encoded_data = base64.b64encode(data)
        return encoded_data
