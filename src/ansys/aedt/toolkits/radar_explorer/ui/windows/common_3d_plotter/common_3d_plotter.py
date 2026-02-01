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

import numpy as np
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from scipy.spatial.transform import Rotation as Rot

from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.toolkits.radar_explorer.rcs_visualization import SceneMeshObjectType
from ansys.aedt.toolkits.radar_explorer.ui.models import properties
from ansys.tools.visualization_interface import Plotter
from ansys.tools.visualization_interface.backends.pyvista import PyVistaBackend


class Common3DPlotter(object):
    def __init__(self, main_window):
        # General properties
        self.main_window = main_window
        self.ui = main_window.ui

        self.dark_mode = True if "dark" in self.main_window.ui.themes["theme_name"] else False
        self.app_color = self.main_window.ui.themes["app_color"]
        self.title_size = properties.font["title_size"]
        self.active_color = self.app_color["text_active"]
        self.background_color = self.app_color["dark_three"]
        self.background_color_title = self.app_color["dark_four"]

        self.window_actors = []

        self.plotter_inst = None
        self.pyvista_3d_container = None
        self.pyvista_3d_layout = None
        self.pv_backend = None
        self.pv_plotter = None
        self.plotter = None

        self.window_placeholders = {}
        self.initialize_plotter()

        self.rotation_active = True

    def get_plotter(self):
        if self.plotter_inst is None:
            self.plotter_inst = self.initialize_plotter()
        return self.plotter_inst

    def initialize_plotter(self):
        if self.pyvista_3d_container is None:
            self.pyvista_3d_container = QWidget()
            self.pyvista_3d_layout = QHBoxLayout(self.pyvista_3d_container)

            self.pv_backend = PyVistaBackend(use_qt=True, show_qt=False)
            self.pv_plotter = Plotter(backend=self.pv_backend)
            self.plotter = self.pv_plotter.backend.pv_interface.scene
            self.pyvista_3d_layout.addWidget(self.plotter)
            self.pv_backend.enable_widgets(dark_mode=self.dark_mode)

            # Disable 'q' key for exiting modeler
            self.plotter.iren.clear_events_for_key("q")

            self.plotter.set_background(color=self.app_color["bg_one"])

            # Default view
            self.plotter.view_xy()
            self.plotter.camera.roll = 90
            self.pyvista_3d_layout.addWidget(self.plotter)

        return self.plotter

    def add_to_window(self, window_name, layout):
        if window_name not in self.window_placeholders:
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.setContentsMargins(0, 0, 0, 0)
            self.window_placeholders[window_name] = placeholder
            layout.addWidget(placeholder)
        self.reparent_to_placeholder(window_name)

    def add_actor(self, actor):
        self.window_actors.append(actor)
        self.plotter.add_actor(actor)

    def clear_window_actors(
        self,
    ):
        actors = self.window_actors.copy()
        for actor in actors:
            self.plotter.remove_actor(actor)
        self.window_actors = []
        self.pv_backend.enable_widgets(dark_mode=self.dark_mode)

    def reparent_to_placeholder(self, window_name):
        if window_name in self.window_placeholders:
            placeholder = self.window_placeholders[window_name]
            if self.pyvista_3d_container.parent() != placeholder:
                self.pyvista_3d_container.setParent(None)
                placeholder.layout().addWidget(self.pyvista_3d_container)

    def plot_model_scene(self):
        # If model comes from the metadata file, we do not need to rotate it again, because it should be already rotated

        self.plotter.suppress_rendering = True
        self.clear_window_actors()
        self.plotter.add_axes_at_origin(labels_off=True)

        # Model
        if self.rotation_active:
            # Get Angle from Incident angle menu
            inc_menu = self.main_window.incident_wave_menu
            angles = [
                Quantity(inc_menu.angle1_textbox.text(), "Angle"),
                Quantity(inc_menu.angle2_textbox.text(), "Angle"),
                Quantity(inc_menu.angle3_textbox.text(), "Angle"),
            ]

            # Convert angles to radians if they are in degrees
            angles = [angle.to("rad") if angle.unit == "deg" else angle for angle in angles]
            rotation_order = inc_menu.rotation_combobox.currentText()

            rot = self.rotation_matrix_from_euler(rotation_order, angles, in_degrees=False)

            # Translation
            pos = [0, 0, 0]

            t = np.concatenate((rot, np.asarray(pos).reshape((-1, 1))), axis=1)
            t = np.concatenate((t, np.array([[0, 0, 0, 1]])), axis=0)
        else:
            t = np.eye(4)

        model = properties.radar_explorer.all_scene_actors["model"]

        for scene in model.values():
            for actor in scene.values():
                options = actor.get_model_options() or {}
                if actor.show:
                    try:
                        # Apply transformation to actor's mesh
                        transformed_mesh = actor.get_mesh().copy()
                        transformed_mesh.transform(t, inplace=True)  # Apply transformation

                        # Add the transformed mesh to the plotter
                        actor_vtk = self.plotter.add_mesh(transformed_mesh, **options)
                        actor.actor = actor_vtk
                        self.add_actor(actor_vtk)

                    except Exception as e:  # pragma: no cover
                        print(f"Failed to add mesh for actor {actor.name}: {e}")

        # Annotations
        annotations = properties.radar_explorer.all_scene_actors["annotations"]
        for scene in annotations.values():
            if scene is not None:
                for actor in scene.values():
                    options = actor.custom_object.get_model_options() or {}
                    try:
                        actor_vtk = self.plotter.add_mesh(actor.mesh, **options)
                        actor.actor = actor_vtk
                        self.add_actor(actor_vtk)

                    except Exception as e:  # pragma: no cover
                        print(f"Failed to add mesh for actor {actor.name}: {e}.")

        # Results

        for _, solutions in properties.radar_explorer.all_scene_actors["results"].items():
            for result_name, result in solutions.items():
                if not hasattr(result, "custom_object"):  # pragma: no cover
                    continue
                options = result.custom_object.get_result_options() or {}
                if result.custom_object.show:
                    try:
                        if "scalar_bar_args" not in options:  # pragma: no cover
                            options["scalar_bar_args"] = {"color": self.active_color, "title": result_name}
                        else:
                            options["scalar_bar_args"]["color"] = self.active_color
                        if result.custom_object.object_type == SceneMeshObjectType.MESH:
                            actor_vtk = self.plotter.add_mesh(result.custom_object.get_mesh(), **options)
                        elif result.custom_object.object_type == SceneMeshObjectType.VOLUME:  # pragma: no cover
                            actor_vtk = self.plotter.add_volume(
                                result.custom_object.get_mesh(), mapper="smart", **options
                            )
                        result.actor = actor_vtk
                        self.add_actor(actor_vtk)
                    except Exception as e:  # pragma: no cover
                        print(f"Failed to add mesh for actor {result.name}: {e}.")

        self.plotter.suppress_rendering = False
        self.plotter.render()

    @staticmethod
    def rotation_matrix_from_euler(rotation_order, angles, in_degrees):
        return Rot.from_euler(rotation_order, angles, in_degrees).as_matrix()
