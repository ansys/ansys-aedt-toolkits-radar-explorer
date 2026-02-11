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

import os
from pathlib import Path
import sys
import time

sys.path.append(str(Path(__file__).parent))

import gc  # noqa: I001

import numpy as np
import pyvista as pv

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.visualization.post.rcs_exporter import MonostaticRCSExporter
from ansys.aedt.toolkits.common.backend.api import AEDTCommon
from ansys.aedt.toolkits.radar_explorer.backend.models import properties
from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.domain_transforms import DomainTransforms


class ToolkitBackend(AEDTCommon):
    """API to control the toolkit workflow.

    This class provides methods to connect to a selected design and create geometries.

    Examples
    --------
    >>> from ansys.aedt.toolkits.radar_explorer.backend.api import ToolkitBackend
    >>> toolkit_api = ToolkitBackend()
    >>> toolkit_api.launch_aedt()
    >>> toolkit_api.wait_to_be_idle()
    """

    def __init__(self):
        """Initialize the ``toolkit`` class."""
        AEDTCommon.__init__(self, properties)
        self.properties = properties
        self.multiplier = 1.0

    def update_rcs_properties(self, range_is_system=True, azimuth_is_system=True, elevation_is_system=True):
        """Update radar setup properties for RCS.

        Parameters
        ----------
        range_is_system : bool, default:`` True``
            Update range properties system based.
        azimuth_is_system : bool, default: ``True``
            Update azimuth properties system based.
        elevation_is_system : bool, default: ``True``
            Update elevation properties system based.

        """
        # Range
        self.__update_range_properties(range_is_system)

        # Azimuth
        self.__update_azimuth_properties(azimuth_is_system)

        # Elevation
        self.__update_elevation_properties(elevation_is_system)

    def update_range_profile_properties(self, is_system=True):
        """Update radar setup properties for range profile.

        Parameters
        ----------
        is_system : bool, default: ``True``
            Update system to performance properties.

        """
        self.__update_range_properties(is_system)

    def update_waterfall_properties(self, range_is_system=True, azimuth_is_system=True):
        """Update radar setup properties for waterfall.

        Parameters
        ----------
        range_is_system : bool, default: ``True``
            Update system to performance properties.
        azimuth_is_system : bool, default: ``True``
            Update azimuth properties system based.
        """
        # Range
        self.__update_range_properties(range_is_system)

        # Azimuth
        self.__update_azimuth_properties(azimuth_is_system)

    def update_isar_2d_properties(self, range_is_system=True, azimuth_is_system=True):
        """Update radar setup properties for the range profile.

        Parameters
        ----------
        range_is_system : bool, default: ``True``
            Update system to performance properties.
        azimuth_is_system : bool, default: ``True``
            Update azimuth properties system based.

        """
        # Range
        self.__update_range_properties(range_is_system)

        # Azimuth
        self.__update_azimuth_properties(azimuth_is_system)

    @staticmethod
    def __update_range_properties(is_system=True):
        center_freq_hz = properties.setup.center_freq
        if is_system:
            # The definition of bandwidth includes the df/2 tails at the extrema of the interval, like in ADP
            bandwidth_hz = properties.setup.fft_bandwidth
            num_freq = properties.setup.num_freq
            delta_freq = bandwidth_hz / num_freq
            num_freq_step = num_freq - 1
            upper_half_bw = num_freq_step // 2 * delta_freq
            lower_half_bw = upper_half_bw if num_freq % 2 == 1 else upper_half_bw + delta_freq
            freq_domain = center_freq_hz + np.linspace(-lower_half_bw, upper_half_bw, num=num_freq)
            dt = DomainTransforms(freq_domain=freq_domain)
        else:
            range_max_tgt = properties.radar.range_max
            range_res_tgt = properties.radar.range_res
            num_range = int(np.ceil(range_max_tgt / range_res_tgt))
            range_domain = np.linspace(0, range_res_tgt * (num_range - 1), num=num_range)
            dt = DomainTransforms(range_domain=range_domain, center_freq=center_freq_hz)

        properties.setup.center_freq = dt.center_freq
        properties.setup.fft_bandwidth = dt.fft_bandwidth
        properties.setup.num_freq = dt.num_freq
        properties.radar.range_res = dt.range_resolution
        properties.radar.range_max = dt.range_period

    @staticmethod
    def __update_azimuth_properties(is_system=True):
        center_freq_hz = properties.setup.center_freq
        if is_system:
            aspect_ang_phi = properties.radar.aspect_ang_phi
            aspect_domain = np.linspace(-aspect_ang_phi / 2, aspect_ang_phi / 2, num=properties.radar.num_phi)
            dt = DomainTransforms(aspect_domain=aspect_domain, center_freq=center_freq_hz)
            properties.radar.range_res_az = dt.range_resolution
            properties.radar.range_max_az = dt.range_period
        else:
            range_max_tgt = properties.radar.range_max_az
            range_res_tgt = properties.radar.range_res_az
            num_range = int(np.ceil(range_max_tgt / range_res_tgt))
            if num_range == 1:
                num_range = 2
            range_domain = np.linspace(0, range_res_tgt * (num_range - 1), num=num_range)
            dt = DomainTransforms(range_domain=range_domain, center_freq=center_freq_hz)
            properties.radar.aspect_ang_phi = dt.aspect_angle
            properties.radar.num_phi = dt.num_aspect_angle

    @staticmethod
    def __update_elevation_properties(is_system=True):
        center_freq_hz = properties.setup.center_freq
        if is_system:
            aspect_ang_theta = properties.radar.aspect_ang_theta
            aspect_domain = np.linspace(-aspect_ang_theta / 2, aspect_ang_theta / 2, num=properties.radar.num_theta)
            dt = DomainTransforms(aspect_domain=aspect_domain, center_freq=center_freq_hz)
            properties.radar.range_res_el = dt.range_resolution
            properties.radar.range_max_el = dt.range_period
        else:
            range_max_tgt = properties.radar.range_max_el
            range_res_tgt = properties.radar.range_res_el
            num_range = int(np.ceil(range_max_tgt / range_res_tgt))
            if num_range == 1:
                num_range = 2
            range_domain = np.linspace(0, range_res_tgt * (num_range - 1), num=num_range)
            dt = DomainTransforms(range_domain=range_domain, center_freq=center_freq_hz)
            properties.radar.aspect_ang_theta = dt.aspect_angle
            properties.radar.num_theta = dt.num_aspect_angle

    def is_sbr_design(self):
        """Check if the design is the SBR+ solution type.

        Returns
        -------
        bool
            Returns ``True`` if it is an SBR+ design, ``False`` otherwise.

        """
        self.connect_design()
        is_sbr = False
        self.logger.info(self.properties.active_design)
        self.logger.info(self.aedtapp.solution_type)
        if self.aedtapp:
            if self.aedtapp.solution_type == "SBR+":
                is_sbr = True
        else:  # pragma: no cover
            self.logger.error("Toolkit cannot connect to AEDT.")
        self.release_aedt(False, False)
        return is_sbr

    def generate_3d_component(self):
        """Generate a 3D component from current design.

        Returns
        -------
        str or bool
            Returns ``True`` if the connection is successful, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.aedt.toolkits.radar_explorer.backend.api import ToolkitBackend
        >>> toolkit_api = ToolkitBackend()
        >>> toolkit_api.launch_aedt()
        >>> toolkit_api.wait_to_be_idle()
        >>> toolkit_api.generate_3d_component()
        """
        self.connect_design()

        if self.aedtapp:
            self.aedtapp.solution_type = "SBR+"
            # Export design to 3D Component
            file_folder = self.aedtapp.working_directory
            base_name = "geo"
            ext = ".a3dcomp"
            file_name = f"{base_name}{ext}"
            component_file = Path(file_folder) / file_name

            increment = 1
            while component_file.is_file():
                file_name = f"{base_name}_{increment}{ext}"
                component_file = Path(file_folder) / file_name
                increment += 1

            # Get available 3D Components
            comp_defs = self.aedtapp.modeler.user_defined_component_names
            obj_names = self.aedtapp.modeler.object_names

            is_created = False
            if len(comp_defs) == 0 and obj_names:  # pragma: no cover
                self.aedtapp.modeler.create_3dcomponent(input_file=str(component_file), excitations=[])
                if component_file.is_file():
                    is_created = True
            else:
                active_project = self.get_project_name(self.properties.active_project)
                is_flattened = self.aedtapp.flatten_3d_components(purge_history=False)
                if self.properties.non_graphical:
                    # In non-graphical mode it is necessary to set the active project and design
                    self.desktop.odesktop.SetActiveProject(active_project)
                    self.release_aedt(False, False)
                    self.connect_design()

                if not is_flattened:  # pragma: no cover
                    self.logger.error("PyAEDT could not flatten the design, remove 3D Components manually.")
                    self.release_aedt(False, False)
                    return False
                is_created = self.aedtapp.modeler.create_3dcomponent(
                    input_file=str(component_file), excitations=[], variables_to_include=[]
                )
            if is_created:
                self.logger.info("3D component created.")
                self.release_aedt(False, False)
                return component_file
            else:  # pragma: no cover
                self.logger.error("3D Component not created.")
                self.release_aedt(False, False)
                return False
        else:  # pragma: no cover
            self.logger.error("Toolkit can not connect to AEDT.")
            self.release_aedt(False, False)
            return False

    def insert_sbr_design(self, input_file, name=None):
        """Insert SBR+ design and insert a component if passed.

        Parameters
        ----------
        input_file : str
            Path of the component file.

        name : str, default: ``None``
            Design name.

        Returns
        -------
        str
            Design name.

        Examples
        --------
        >>> from ansys.aedt.toolkits.radar_explorer.backend.api import ToolkitBackend
        >>> toolkit_api = ToolkitBackend()
        >>> toolkit_api.launch_aedt()
        >>> toolkit_api.wait_to_be_idle()
        >>> toolkit_api.insert_sbr_design()
        """
        self.connect_design()

        if self.aedtapp:
            if not name:
                name = generate_unique_name(self.aedtapp.design_name)
            self.aedtapp.insert_design(name=name, solution_type="SBR+")
            design_name = self.aedtapp.design_name
            self.properties.active_design = design_name
            self.save_project(release_aedt=False)
            # Set active design after reload project
            self.properties.active_design = design_name
            self.aedtapp.modeler.model_units = properties.cad.model_units
            self.logger.info(f"SBR design inserted: {self.properties.active_design}.")
            self.logger.debug("Add coordinate system parameters.")
            self.aedtapp["rot_ang1"] = f"{properties.radar.rotation_ang1}deg"
            self.aedtapp["rot_ang2"] = f"{properties.radar.rotation_ang2}deg"
            self.aedtapp["rot_ang3"] = f"{properties.radar.rotation_ang3}deg"
            cs = self.aedtapp.modeler.create_coordinate_system(
                mode=properties.radar.rotation_order.lower(), phi="rot_ang1", theta="rot_ang2", psi="rot_ang3"
            )
            self.aedtapp.modeler.insert_3d_component(input_file=input_file, coordinate_system=cs.name)
            self.logger.info("3D Component inserted.")
            self.save_project(release_aedt=True, project_path=self.properties.active_project)
            # Set active design after reload project
            self.properties.active_design = design_name
            return design_name
        else:  # pragma: no cover
            self.logger.error("Toolkit can not connect to AEDT.")
            self.release_aedt(False, False)
            return False

    def insert_cad_sbr(self, name=None):
        """Insert CAD in the SBR+ design.

        Parameters
        ----------
        name : str, default: ``None``
            New design name.

        Returns
        -------
        str
            Design name.
        """
        if not properties.cad.input_file:  # pragma: no cover
            self.logger.error("No CAD files added.")
            return False
        cad_files = properties.cad.input_file
        materials = properties.cad.material
        positions = properties.cad.position
        if properties.cad.material and len(materials) != len(cad_files):
            self.logger.error("Number of materials must be the same as in CAD files.")
            return False
        elif not materials:
            materials = ["pec"] * len(cad_files)

        if properties.cad.position and len(positions) != len(cad_files):
            self.logger.error("Number of positions must be the same as in CAD files.")
            return False
        elif not positions:
            positions = [[0, 0, 0]] * len(cad_files)

        self.connect_design()

        if self.aedtapp:
            self.aedtapp.modeler.model_units = properties.cad.model_units
            if not name:
                name = generate_unique_name(self.aedtapp.design_name)
            if name in self.aedtapp.design_list:  # pragma: no cover
                name = self.aedtapp._generate_unique_design_name(name)
            self.aedtapp.insert_design(name=name, solution_type="SBR+")
            self.aedtapp.modeler.model_units = properties.cad.model_units
            design_name = self.aedtapp.design_name
            self.properties.active_design = design_name

            self.save_project(release_aedt=False)
            # Set active design after reload project
            self.properties.active_design = design_name

            self.logger.info(f"SBR design inserted: {self.properties.active_design}.")

            # Insert CAD

            for cont_file, cad_file in enumerate(cad_files):
                cad_file = Path(cad_file)
                material = materials[cont_file]
                position = positions[cont_file]

                path = Path(self.aedtapp.toolkit_directory)
                file = cad_file.stem
                extension = cad_file.suffix
                new_file_name = file + ".stl"
                new_file_name_obj = file + ".obj"

                new_file_full_path = path / new_file_name
                new_file_full_path_obj = path / new_file_name_obj

                # Convert to STL
                if extension == ".obj":
                    reader = pv.get_reader(cad_file)
                    obj_mesh = reader.read()
                    obj_mesh.save(new_file_full_path)
                    cad_file = new_file_full_path
                elif extension == ".gltf" or extension == ".glb":
                    pl = pv.Plotter()
                    pl.import_gltf(cad_file)
                    pl.export_obj(new_file_full_path_obj)

                    reader = pv.get_reader(new_file_full_path_obj)
                    obj_mesh = reader.read()
                    obj_mesh.save(new_file_full_path)
                    cad_file = new_file_full_path

                new_extension = cad_file.suffix
                old_model_objects = self.aedtapp.modeler.model_objects

                if new_extension == ".stl" and cad_file.is_file():
                    self.aedtapp.modeler.import_3d_cad(str(cad_file), create_lightweigth_part=True)
                else:  # pragma: no cover
                    self.logger.error("Wrong CAD format.")
                    self.release_aedt(False, False)
                    return False

                new_models = self.aedtapp.modeler.model_objects
                new_model_objects = [solid for solid in new_models if solid not in old_model_objects]

                for new_model in new_model_objects:
                    model_object = self.aedtapp.modeler[new_model]
                    if model_object.object_type == "Sheet":
                        if material == "pec":
                            self.aedtapp.assign_perfecte_to_sheets(model_object)
                        else:
                            self.aedtapp.assign_finite_conductivity(model_object, material=material)
                    elif model_object.object_type == "Solid":  # pragma: no cover
                        model_object.material_name = material
                    model_object.move(position)

            # Replace 3D Component
            self.aedtapp.modeler.replace_3dcomponent(name="rcs_scenario", assignment=self.aedtapp.modeler.model_objects)

            self.logger.info("3D Component inserted.")

            self.logger.debug("Add coordinate system parameters.")
            self.aedtapp["rot_ang1"] = f"{properties.radar.rotation_ang1}deg"
            self.aedtapp["rot_ang2"] = f"{properties.radar.rotation_ang2}deg"
            self.aedtapp["rot_ang3"] = f"{properties.radar.rotation_ang3}deg"
            cs = self.aedtapp.modeler.create_coordinate_system(
                mode=properties.radar.rotation_order.lower(), phi="rot_ang1", theta="rot_ang2", psi="rot_ang3"
            )

            component_name = self.aedtapp.modeler.user_defined_component_names[0]
            component = self.aedtapp.modeler.user_defined_components[component_name]
            component.target_coordinate_system = cs.name

            self.save_project(release_aedt=True, project_path=self.properties.active_project)

            # Set active design after reload project
            self.properties.active_design = design_name
            return design_name
        else:  # pragma: no cover
            self.logger.error("Toolkit cannot connect to AEDT.")
            self.release_aedt(False, False)
            return False

    def duplicate_sbr_design(self, name=None):
        """Duplicate an existing SBR+ design.

        Parameters
        ----------
        name : str, default: ``None``
            New design name.

        Returns
        -------
        str
            Design name.
        """
        self.connect_design()
        if self.aedtapp:
            self.aedtapp.duplicate_design(self.aedtapp.design_name)
            self.save_project(release_aedt=False)
            self.logger.info("SBR design duplicated.")

            # Check if Native solids exist to convert them to 3D Components
            solids_in_components = []
            for model_object in self.aedtapp.modeler.user_defined_components.values():
                for part in model_object.parts:
                    solids_in_components.append(part)

            # Convert native object to 3D Component
            solids_to_component = []
            for model_part in self.aedtapp.modeler.objects:
                if model_part not in solids_in_components:
                    solids_to_component.append(self.aedtapp.modeler.objects[model_part].name)
            if solids_to_component:
                _ = self.aedtapp.modeler.replace_3dcomponent(assignment=solids_to_component)

            self.logger.debug("Add coordinate system parameters.")
            self.aedtapp["rot_ang1"] = f"{properties.radar.rotation_ang1}deg"
            self.aedtapp["rot_ang2"] = f"{properties.radar.rotation_ang2}deg"
            self.aedtapp["rot_ang3"] = f"{properties.radar.rotation_ang3}deg"
            cs = self.aedtapp.modeler.create_coordinate_system(
                mode=properties.radar.rotation_order.lower(), phi="rot_ang1", theta="rot_ang2", psi="rot_ang3"
            )

            for model_object in self.aedtapp.modeler.user_defined_components.values():
                model_object.target_coordinate_system = cs.name

            if name:
                self.aedtapp.design_name = name

            design_name = self.aedtapp.design_name
            self.save_project(release_aedt=True)
            return design_name
        else:  # pragma: no cover
            self.logger.error("Toolkit can not connect to AEDT.")
            self.release_aedt(False, False)
            return False

    def add_plane_wave(self, name="IncPWave1", polarization="Vertical"):
        """Insert plane wave.

        Parameters
        ----------
        name : str, default: ``None``
            Name of the plane wave.
        polarization : str, default: ``"Vertical"``
            Polarization type. Options are ``"Horizontal"``
            and ``"Vertical"``.

        Returns
        -------
        str
            Plane wave name.

        Examples
        --------
        >>> from ansys.aedt.toolkits.radar_explorer.backend.api import ToolkitBackend
        >>> toolkit_api = ToolkitBackend()
        >>> toolkit_api.launch_aedt()
        >>> toolkit_api.wait_to_be_idle()
        >>> toolkit_api.add_plane_wave()
        """
        self.connect_design()

        if self.aedtapp:
            calc_type = properties.radar.calculation_type

            if calc_type == "Range Profile":  # pragma: no cover
                phi_start = 0
                phi_stop = 0
                num_phi = 1
                theta_start = 90
                theta_stop = 90
                num_theta = 1
            elif calc_type == "2D ISAR":  # pragma: no cover
                phi_start = -properties.radar.aspect_ang_phi / 2
                phi_stop = +properties.radar.aspect_ang_phi / 2
                num_phi = properties.radar.num_phi
                theta_start = 90
                theta_stop = 90
                num_theta = 1
            else:
                phi_start = -properties.radar.aspect_ang_phi / 2
                phi_stop = +properties.radar.aspect_ang_phi / 2
                num_phi = properties.radar.num_phi
                theta_start = -properties.radar.aspect_ang_theta / 2 + 90
                theta_stop = +properties.radar.aspect_ang_theta / 2 + 90
                num_theta = properties.radar.num_theta

            e_theta = {"Vertical": 1, "Horizontal": 0}
            e_phi = {"Vertical": 0, "Horizontal": 1}

            propagation_vector = [
                [str(phi_start) + "deg", str(phi_stop) + "deg", num_phi],
                [str(theta_start) + "deg", str(theta_stop) + "deg", num_theta],
            ]

            plane_wave = self.aedtapp.plane_wave(
                vector_format="Spherical",
                origin=None,
                polarization=[e_phi[polarization], e_theta[polarization]],
                propagation_vector=propagation_vector,
                wave_type="Propagating",
                wave_type_properties=None,
                name=name,
            )
            plane_wave_name = plane_wave.name
            if not properties.setup.plane_wave_names:
                properties.setup.plane_wave_names = plane_wave_name
            else:
                properties.setup.plane_wave_names += ", " + plane_wave_name
            self.logger.info(f"Plane wave {plane_wave_name} created.")
            self.release_aedt(False, False)

            return plane_wave_name

        else:  # pragma: no cover
            self.logger.error("Toolkit can not connect to AEDT.")
            self.release_aedt(False, False)
            return False

    def add_setup(self, name=None):
        """Insert setup.

        Parameters
        ----------
        name : str, default: ``None``
            Name of the setup.

        Returns
        -------
        str
            Setup name.

        Examples
        --------
        >>> from ansys.aedt.toolkits.radar_explorer.backend.api import ToolkitBackend
        >>> toolkit_api = ToolkitBackend()
        >>> toolkit_api.launch_aedt()
        >>> toolkit_api.wait_to_be_idle()
        >>> toolkit_api.add_sbr_setup()
        """
        self.connect_design()

        if self.aedtapp:
            if not name:
                name = properties.setup.setup_name
            ray_density = properties.setup.ray_density
            num_bounces = properties.setup.num_bounces
            ffl = properties.setup.ffl
            ptd_utd = properties.setup.ptd_utd
            num_freq = properties.setup.num_freq
            # note that simulation frequency is not fft frequency
            start_freq_ghz = properties.setup.sim_freq_lower * 1e-9
            end_freq_ghz = properties.setup.sim_freq_upper * 1e-9

            ptd_option = None
            if ptd_utd:
                ptd_option = "PTD Correction + UTD Rays"

            setup = self.aedtapp.create_setup(
                name=name,
                MaxNumberOfBounces=num_bounces,
                RayDensityPerWavelength=ray_density,
                FastFrequencyLooping=ffl,
                PTDUTDSimulationSettings=ptd_option,
            )
            setup.auto_update = False
            setup.props["ComputeFarFields"] = True
            setup.props["IsMonostaticRCS"] = True
            setup.update()
            setup.props["Sweeps"]["Sweep"]["RangeType"] = "LinearCount"
            setup.props["Sweeps"]["Sweep"]["RangeStart"] = str(start_freq_ghz) + "GHz"
            setup.props["Sweeps"]["Sweep"]["RangeEnd"] = str(end_freq_ghz) + "GHz"
            setup.props["Sweeps"]["Sweep"]["RangeCount"] = num_freq
            setup.update()

            setup_name = setup.name
            properties.setup.setup_name = setup_name
            if len(self.aedtapp.modeler.coordinate_systems) != 0:
                # Update CS
                cs = self.aedtapp.modeler.coordinate_systems[0]
                if cs.props["Mode"] != "Axis/Position":
                    if properties.radar.rotation_order == "ZYZ":
                        cs.props["Mode"] = "Euler Angle ZYZ"
                    else:
                        cs.props["Mode"] = "Euler Angle ZXZ"
                    self.aedtapp["rot_ang1"] = f"{properties.radar.rotation_ang1}deg"
                    self.aedtapp["rot_ang2"] = f"{properties.radar.rotation_ang2}deg"
                    self.aedtapp["rot_ang3"] = f"{properties.radar.rotation_ang3}deg"

            self.logger.info(f"Setup {setup_name} created.")
            self.release_aedt(False, False)
            return setup_name

        else:  # pragma: no cover
            self.logger.error("Toolkit can not connect to AEDT.")
            self.release_aedt(False, False)
            return False

    def analyze(self):  # pragma: no cover
        """Analyze the design.

        Launch analysis. AEDT is released once it is opened.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> import time
        >>> from ansys.aedt.toolkits.radar.backend.api import ToolkitBackend
        >>> toolkit = ToolkitBackend()
        >>> msg1 = toolkit_api.launch_thread(toolkit.launch_aedt)
        >>> idle = toolkit_api.wait_to_be_idle()
        >>> toolkit.analyze()
        """
        self.connect_design()

        if self.aedtapp:
            num_cores = properties.setup.num_cores

            self.aedtapp.save_project()

            if not self.properties.setup.solve_interactive and not self.properties.non_graphical:  # pragma: no cover
                active_design = self.properties.active_design
                self.release_aedt(True, True)
                self.properties.selected_process = 0
                self.properties.non_graphical = True
                self.launch_aedt()
                self.open_project()
                self.properties.active_design = active_design
                self.connect_design()

            self.aedtapp.analyze(cores=num_cores, blocking=False)

            while True:
                if not self.aedtapp.are_there_simulations_running:
                    break
                else:
                    time.sleep(1)

            gc.collect()
            self.release_aedt(False, False)

            return True

        else:  # pragma: no cover
            self.logger.error("Toolkit can not connect to AEDT.")
            self.release_aedt(False, False)
            return False

    def export_rcs(self, excitation=None, expression=None, encode=False):
        """Get RCS data.

        Parameters
        ----------
        excitation : str, default: ``None``
            Excitation name.
        expression : str, default: ``None``
            Expression name.
        encode : bool, default: ``False``
            Whether to encode the file.

        Returns
        -------
        list or str
            Metadata file path.
        """
        self.connect_design()

        if self.aedtapp:
            if expression or excitation:
                setup_name = properties.setup.setup_name
                sweep_name = properties.setup.sweep_name
                setup_sweep_name = f"{setup_name} : {sweep_name}"
                variations = self.aedtapp.available_variations.nominal_w_values_dict_w_dependent

                excitations = self.aedtapp.excitations
                if len(excitations) > 1:
                    if excitation == excitations[0]:
                        self.aedtapp.edit_sources(assignment={excitations[0]: "1", excitations[1]: "0"})
                    else:
                        self.aedtapp.edit_sources(assignment={excitations[0]: "0", excitations[1]: "1"})

                rcs_data = self.aedtapp.post.get_solution_data(
                    expressions=expression,
                    variations=variations,
                    setup_sweep_name=setup_sweep_name,
                    report_category="Monostatic RCS",
                )
                frequencies = None
                if rcs_data and getattr(rcs_data, "primary_sweep_values", None) is not None:
                    frequencies = list(rcs_data.primary_sweep_values)

                rcs = MonostaticRCSExporter(
                    self.aedtapp,
                    setup_name=setup_sweep_name,
                    frequencies=frequencies,
                    expression=expression,
                )
                if excitation == "IncWaveHpol":
                    if expression == "ComplexMonostaticRCSTheta":  # pragma: no cover
                        metadata_name = "VH"
                        data_name = "VH_data"
                    else:
                        metadata_name = "HH"
                        data_name = "HH_data"
                else:
                    if expression == "ComplexMonostaticRCSTheta":
                        metadata_name = "VV"
                        data_name = "VV_data"
                    else:
                        metadata_name = "HV"
                        data_name = "HV_data"
                rcs.column_name = metadata_name
                rcs.export_rcs(name=data_name, metadata_name=metadata_name)
                if encode:
                    encoded_json_file = None
                    encoded_geometry_files = []

                    metadata_file = rcs.metadata_file
                    metadata_dir = Path(metadata_file).parent
                    if Path(metadata_file).is_file():
                        serialized_file = self.serialize_obj_base64(metadata_file)
                        encoded_json_file = serialized_file.decode("utf-8")
                    geometry_path = (metadata_dir / "geometry").resolve()
                    if geometry_path.exists():
                        for root, _, files in os.walk(geometry_path):
                            for file in files:
                                if file.lower().endswith(".obj"):
                                    geometry_file = (Path(root) / file).resolve()
                                    serialized_file = self.serialize_obj_base64(geometry_file)
                                    encoded_geometry_files.append(serialized_file.decode("utf-8"))
                    data_file = Path(rcs.data_file).resolve()
                    serialized_file = self.serialize_obj_base64(data_file)
                    encoded_rcs_file = serialized_file.decode("utf-8")
                    return encoded_json_file, encoded_geometry_files, encoded_rcs_file
                self.release_aedt(False, False)
                return rcs.metadata_file

            else:
                rcs = MonostaticRCSExporter(self.aedtapp)
                rcs.export_rcs(name="Geometry", metadata_name="geo", only_geometry=True)
                if encode:
                    encoded_json_file = None
                    encoded_geometry_files = []

                    metadata_file = rcs.metadata_file
                    metadata_dir = Path(metadata_file).parent
                    if Path(metadata_file).is_file():
                        serialized_file = self.serialize_obj_base64(metadata_file)
                        encoded_json_file = serialized_file.decode("utf-8")
                    geometry_path = (metadata_dir / "geometry").resolve()
                    if geometry_path.exists():
                        for root, _, files in os.walk(geometry_path):
                            for file in files:
                                if file.lower().endswith(".obj"):
                                    geometry_file = (Path(root) / file).resolve()
                                    serialized_file = self.serialize_obj_base64(geometry_file)
                                    encoded_geometry_files.append(serialized_file.decode("utf-8"))
                    encoded_rcs_file = None
                    self.release_aedt(False, False)
                    return encoded_json_file, encoded_geometry_files, encoded_rcs_file
                self.release_aedt(False, False)
                return rcs.metadata_file

        else:  # pragma: no cover
            self.logger.error("Toolkit cannot connect to AEDT.")
            self.release_aedt(False, False)
            return False

    def get_setups(self):
        """Get setups."""
        if not self.aedtapp:
            self.connect_design()
        available_setups = []
        if self.aedtapp:
            available_setups = self.aedtapp.setup_names
            self.release_aedt(False, False)
        return available_setups

    def get_sweeps(self):
        """Get sweeps."""
        if not self.aedtapp:
            self.connect_design()

        sweeps = ["Sweep"]
        if self.aedtapp and not self.aedtapp.solution_type == "SBR+" and properties.setup.setup_name != "No Setup":
            setup = self.aedtapp.get_setup(properties.setup.setup_name)
            sweeps = ["LastAdaptive"]
            if setup:
                setup_sweeps = setup.get_sweep_names()
                sweeps.extend(setup_sweeps)
            self.release_aedt(False, False)
        return sweeps

    def get_plane_waves(self):
        """Get plane waves."""
        if not self.aedtapp:
            self.connect_design()
        available_setups = []
        if self.aedtapp:
            available_setups = self.aedtapp.excitations
            self.release_aedt(False, False)
        return available_setups

    def get_materials(self):
        """Get available materials."""
        if not self.aedtapp:
            self.connect_design()
        final_materials = []
        if self.aedtapp:
            materials = self.aedtapp.materials.mat_names_aedt
            materials = [m for m in materials if not m.startswith("$")]
            filtered = list(dict.fromkeys(materials))
            final_materials = sorted(filtered, key=lambda x: (x.lower() != "pec", x[0].isupper(), x.lower(), x))

            self.release_aedt(False, False)
        return final_materials
