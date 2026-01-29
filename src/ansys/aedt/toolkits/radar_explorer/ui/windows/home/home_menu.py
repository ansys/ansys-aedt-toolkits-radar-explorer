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

import ast
from pathlib import Path

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.toolkits.common.ui.utils.widgets import PyIconButton
from matplotlib import colormaps
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.utils import unit_converter_rcs
from ansys.aedt.toolkits.radar_explorer.ui.models import properties
from ansys.aedt.toolkits.radar_explorer.ui.windows.common_3d_plotter.common_3d_plotter import Common3DPlotter
from ansys.aedt.toolkits.radar_explorer.ui.windows.common_windows_utils import CommonWindowUtilsRCS
from ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_column import Ui_HomeColumn
from ansys.aedt.toolkits.radar_explorer.ui.windows.home.home_page import Ui_Home

PROJECTION_CATEGORIES_LIST = ["Perspective", "Orthographic"]
AVAILABLE_UNITS = ["meter", "dm", "cm", "mm", "um", "nm", "mil", "ft"]


class ImportCADThread(QThread):
    finished_signal = Signal(bool)

    def __init__(self, app, input_file, material, position, units):
        super().__init__()
        self.main_window = app.main_window
        self.cad_file = input_file
        self.material = material
        self.position = position
        self.model_units = units
        self.metadata_file = None

    def run(self):
        insert_cad_flag = self.main_window.insert_cad_design(
            input_file=self.cad_file, material=self.material, position=self.position, units=self.model_units
        )
        if not insert_cad_flag:
            self.finished_signal.emit(insert_cad_flag)

        self.metadata_file = self.main_window.export_rcs()

        self.finished_signal.emit(self.metadata_file)


class DuplicateDesignThread(QThread):
    finished_signal = Signal(bool)

    def __init__(self, app):
        super().__init__()
        self.main_window = app.main_window
        self.metadata_file = None

    def run(self):
        component_file = self.main_window.generate_3d_component()

        if not component_file:
            self.finished_signal.emit(False)
            return False
        be_properties = self.main_window.get_properties()
        design_list = be_properties["design_list"]
        name = "RCS_Design"
        found = any("RCS_Design" in value for values in design_list.values() for value in values)
        if found:
            name = generate_unique_name(name)
        self.main_window.insert_sbr_design(component_file, name)
        self.metadata_file = self.main_window.export_rcs()
        self.finished_signal.emit(self.metadata_file)


class HomeMenu(object):
    def __init__(self, main_window):
        # General properties
        self.class_name = "HomeMenu"
        self.main_window = main_window
        self.ui = main_window.ui
        self.dark_mode = True if "dark" in self.main_window.ui.themes["theme_name"] else False
        self.app_color = self.main_window.ui.themes["app_color"]
        self.title_size = self.main_window.properties.font["title_size"]
        self.combo_size = self.main_window.properties.font["combo_size"]
        self.active_color = self.app_color["text_active"]
        self.background_color = self.app_color["dark_three"]
        self.background_color_title = self.app_color["dark_four"]
        self.is_loaded = False
        self.file_mode = True
        self.is_independent = False

        # Add left column
        new_ui = Ui_HomeColumn()
        new_column_widget = QWidget()
        new_ui.setupUi(new_column_widget)

        self.ui.left_column.menus.menus.addWidget(new_column_widget)
        self.home_column_widget = new_column_widget
        self.home_column_vertical_layout = new_ui.home_vertical_layout

        self.file_mode_layout = QHBoxLayout()

        self.aedt_toggle_layout = QHBoxLayout()

        self.aedt_settings_layout = None
        self.aedt_settings_button = None

        self.toggle = None
        self.aedt_toggle = None

        self.solved_toggle_layout = QHBoxLayout()
        self.solved_toggle = None

        self.browse_file_group = None
        self.browse = None
        self.file = None

        self.aedt_mode_layout = QVBoxLayout()

        self.project_label = None
        self.project_combobox = None
        self.project_combo_widget = None

        self.load_rcs_layout = None
        self.load_rcs_button = None

        self.projection_menu_layout = None
        self.projection_menu = None
        self.projection_menu_label = None

        self.rcs_object = {}

        # Column
        self.x_origin_label = None
        self.x_position = None

        # Add page
        home_menu_index = self.ui.add_page(Ui_Home)
        self.ui.load_pages.pages.setCurrentIndex(home_menu_index)
        self.home_menu_widget = self.ui.load_pages.pages.currentWidget()

        self.home_label = None
        self.home_layout = None

        # 3D Plotter
        self.pyvista_home_container = None
        self.pyvista_home_layout = None
        self.pv_plotter = None
        self.pv_backend = None
        self.plotter = Common3DPlotter(self.main_window)

        # Model settings
        self.model_settings_column_label = None
        self.post_settings_column_label = None
        self.model_settings_label = None
        self.model_setting_icon = None
        self.model_loaded_tree = None
        self.model_units_menu_layout = None
        self.model_units_menu_label = None
        self.model_unit_menu = None
        self.post_3d_loaded_tree = None
        self.post_3d_delete_button_layout = None
        self.post_3d_delete_button = None
        self.separator1 = None
        self.separator2 = None
        self.separator3 = None

        # Threads
        self.import_cad_thread = None
        self.duplicate_design_thread = None

        # Common RCS Utils
        self.rcs_utils = CommonWindowUtilsRCS(self.main_window.ui.themes)

    def setup(self):
        # Left Column

        # Mode Layout
        self.home_column_vertical_layout.addLayout(self.file_mode_layout)
        self.__setup_toggle()
        self.toggle.stateChanged.connect(self.toggle_state_changed)

        spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.home_column_vertical_layout.addItem(spacer)

        # Open Settings connect AEDT
        row_returns = self.ui.add_n_buttons(
            self.home_column_vertical_layout,
            num_buttons=1,
            height=40,
            width=[180],
            text=["AEDT Settings"],
            font_size=self.title_size,
        )

        self.aedt_settings_layout = row_returns[0]
        self.aedt_settings_button = row_returns[1]
        self.aedt_settings_button.setEnabled(True)
        self.aedt_settings_button.clicked.connect(self.main_window.settings_menu_clicked)

        self.ui.add_vertical_line(self.home_column_vertical_layout, [0, 20], [0, 10])

        # AEDT Mode
        self.home_column_vertical_layout.addLayout(self.aedt_toggle_layout)

        spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.home_column_vertical_layout.addItem(spacer)

        self.__aedt_setup_toggle()
        self.aedt_toggle.stateChanged.connect(self.aedt_toggle_state_changed)

        spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.home_column_vertical_layout.addItem(spacer)

        # Add Open file
        self.__open_file()
        self.browse.clicked.connect(lambda: self.browse_file())

        spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.home_column_vertical_layout.addItem(spacer)

        # AEDT Mode combobox
        self.home_column_vertical_layout.addLayout(self.aedt_mode_layout)
        self.__setup_aedt_comboboxes()

        self.ui.add_vertical_line(self.home_column_vertical_layout, [0, 20], [0, 10])

        # Load information
        self.load_button()
        self.load_rcs_button.setEnabled(False)
        self.load_rcs_button.clicked.connect(self.load_rcs)

        self.ui.add_vertical_line(self.home_column_vertical_layout, [0, 10])

        # Page

        # Style
        self.home_label = self.home_menu_widget.findChild(QLabel, "home_label")
        self.home_layout = self.home_menu_widget.findChild(QVBoxLayout, "home_layout")
        home_label_style = """
        QLabel {{color: {_color}; font-size: {_font_size}pt;
        font-weight: bold;
        }}
        """
        custom_style = home_label_style.format(
            _color=self.app_color["text_active"], _bg_color=self.app_color["dark_three"], _font_size=self.title_size
        )
        self.home_label.setStyleSheet(custom_style)

        # 3D Scene
        self.initialize_plotter()

        # Home page as first page
        welcome_label = self.ui.load_pages.home_page.findChild(QLabel, "label")
        # Add welcome message
        message = properties.welcome_message
        welcome_label.setText(message)

        # Add logo to main page depending on the theme, we can change the logo to white or black version
        if not properties.logo:
            main_window_logo = self.ui.images_load.image_path("ansys-primary-logo-black.svg")
            if self.ui.themes["theme_name"] == "ansys_dark":
                main_window_logo = self.ui.images_load.image_path("ansys-primary-logo-white.svg")
        else:
            main_window_logo = properties.logo
        main_logo = QSvgWidget(main_window_logo)
        self.ui.load_pages.logo_layout.addWidget(main_logo, Qt.AlignCenter, Qt.AlignCenter)

        main_logo.setFixedSize(240, 120)

        if self.model_settings_label is None:
            self.model_3d_settings_setup()

    # Column calls
    def browse_file(self):
        if not self.toggle.isChecked():
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog

            file, _ = QFileDialog.getOpenFileName(
                self.ui.app,
                "QFileDialog.getOpenFileName()",
                "",
                "Metadata File (*.json)",
                options=options,
            )
            if file != "":
                self.file.setText(file)
                self.load_rcs_button.setEnabled(True)
        else:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog

            file, _ = QFileDialog.getOpenFileName(
                self.ui.app,
                "QFileDialog.getOpenFileName()",
                "",
                "All Supported Files (*.stl *.obj *.gltf *.glb) "
                ";;STL Files (*.stl);;OBJ Files (*.obj);;GLTF "
                "Files (*.gltf);;GLB Files (*.glb)",
                options=options,
            )

            if file != "":
                self.file.setText(file)
                self.load_rcs_button.setEnabled(True)

    def load_button(self):
        row_returns = self.ui.add_n_buttons(
            self.home_column_vertical_layout,
            num_buttons=1,
            height=40,
            width=[180],
            text=["Load"],
            font_size=self.title_size,
        )

        self.load_rcs_layout = row_returns[0]
        self.load_rcs_button = row_returns[1]

    def toggle_state_changed(self):
        if self.toggle.isChecked():
            self.ui.update_logger("AEDT mode menu")
            self.file_mode = False
            self.__show_layout_widgets(self.load_design_select_row, True)
            self.__show_layout_widgets(self.project_combo_widget, True)
            self.__show_layout_widgets(self.design_combo_widget, True)
            self.__show_layout_widgets(self.rcs_setup_combo_widget, True)
            self.__show_layout_widgets(self.setup_combo_widget, True)
            self.__show_layout_widgets(self.sweep_combo_widget, True)
            self.__show_layout_widgets(self.expression_combo_widget, True)
            self.__show_layout_widgets(self.solved_toggle_layout, True)
            self.__show_layout_widgets(self.browse_file_group, False)
            self.__show_layout_widgets(self.solution_select_row, True)
            self.__show_layout_widgets(self.material_widget, False)
            self.__show_layout_widgets(self.origin_x_widget, False)
            self.__show_layout_widgets(self.origin_y_widget, False)
            self.__show_layout_widgets(self.origin_z_widget, False)
        else:
            self.ui.update_logger("File mode menu")
            self.file_mode = True
            self.__show_layout_widgets(self.load_design_select_row, False)
            self.__show_layout_widgets(self.project_combo_widget, False)
            self.__show_layout_widgets(self.design_combo_widget, False)
            self.__show_layout_widgets(self.setup_combo_widget, False)
            self.__show_layout_widgets(self.sweep_combo_widget, False)
            self.__show_layout_widgets(self.expression_combo_widget, False)
            self.__show_layout_widgets(self.rcs_setup_combo_widget, False)
            self.__show_layout_widgets(self.solved_toggle_layout, False)
            self.__show_layout_widgets(self.browse_file_group, True)
            self.__show_layout_widgets(self.solution_select_row, False)
            self.__show_layout_widgets(self.material_widget, False)
            self.__show_layout_widgets(self.origin_x_widget, False)
            self.__show_layout_widgets(self.origin_y_widget, False)
            self.__show_layout_widgets(self.origin_z_widget, False)

    def aedt_toggle_state_changed(self):
        if self.aedt_toggle.isChecked():
            self.ui.update_logger("Import geometry menu")
            self.__show_layout_widgets(self.project_combo_widget, False)
            self.__show_layout_widgets(self.design_combo_widget, False)
            self.__show_layout_widgets(self.setup_combo_widget, False)
            self.__show_layout_widgets(self.sweep_combo_widget, False)
            self.__show_layout_widgets(self.rcs_setup_combo_widget, False)
            self.__show_layout_widgets(self.expression_combo_widget, False)
            self.__show_layout_widgets(self.browse_file_group, True)
            self.__show_layout_widgets(self.solution_select_row, False)
            self.__show_layout_widgets(self.material_widget, True)
            self.__show_layout_widgets(self.origin_x_widget, True)
            self.__show_layout_widgets(self.origin_y_widget, True)
            self.__show_layout_widgets(self.origin_z_widget, True)
            self.__show_layout_widgets(self.solved_toggle_layout, False)
        else:
            self.ui.update_logger("Load design menu")
            self.__show_layout_widgets(self.project_combo_widget, True)
            self.__show_layout_widgets(self.design_combo_widget, True)
            self.__show_layout_widgets(self.setup_combo_widget, True)
            self.__show_layout_widgets(self.sweep_combo_widget, True)
            self.__show_layout_widgets(self.expression_combo_widget, True)
            self.__show_layout_widgets(self.rcs_setup_combo_widget, True)
            self.__show_layout_widgets(self.browse_file_group, False)
            self.__show_layout_widgets(self.solution_select_row, True)
            self.__show_layout_widgets(self.material_widget, False)
            self.__show_layout_widgets(self.origin_x_widget, False)
            self.__show_layout_widgets(self.origin_y_widget, False)
            self.__show_layout_widgets(self.origin_z_widget, False)
            self.__show_layout_widgets(self.solved_toggle_layout, True)
            self.solved_toggle_state_changed()

    def solved_toggle_state_changed(self):
        if self.solved_toggle.isChecked():
            self.ui.update_logger("New solution")
            self.__show_layout_widgets(self.project_combo_widget, True)
            self.__show_layout_widgets(self.design_combo_widget, True)
            self.__show_layout_widgets(self.setup_combo_widget, False)
            self.__show_layout_widgets(self.sweep_combo_widget, False)
            self.__show_layout_widgets(self.rcs_setup_combo_widget, False)
            self.__show_layout_widgets(self.expression_combo_widget, False)
            self.__show_layout_widgets(self.browse_file_group, False)

        else:
            self.ui.update_logger("Get solution")
            self.__show_layout_widgets(self.project_combo_widget, True)
            self.__show_layout_widgets(self.design_combo_widget, True)
            self.__show_layout_widgets(self.setup_combo_widget, True)
            self.__show_layout_widgets(self.sweep_combo_widget, True)
            self.__show_layout_widgets(self.expression_combo_widget, True)
            self.__show_layout_widgets(self.rcs_setup_combo_widget, True)
            self.__show_layout_widgets(self.browse_file_group, False)

    def load_rcs(self):
        if self.file_mode:
            self.ui.update_progress(0)
            self.ui.update_logger("Loading RCS information")
            input_file = self.file.text()

            # Check if it is metadata or configuration file
            data = read_json(input_file)
            if not data.get("metadata_files", None) and data.get("model_info", None):
                # The file is a metadata
                self.load_rcs_metadatada(input_file)
                self.is_independent = True
                self.main_window.mode_select_menu.set_options_enabled(False)
                self.main_window.incident_wave_menu.set_options_enabled(False)
                self.main_window.solver_setup_menu.set_options_enabled(False)
                self.disable_options()
            else:
                # File is a configuration file
                metadata_files = data.get("metadata_files", [])

                for prop_name, prop_value in data.items():
                    if hasattr(properties.radar_explorer, prop_name):
                        setattr(properties.radar_explorer, prop_name, prop_value)
                self.main_window.incident_wave_menu.load_status()
                self.main_window.mode_select_menu.load_status()
                self.main_window.solver_setup_menu.load_status()
                if metadata_files:
                    self.plotter.rotation_active = False
                    for metadata_file in metadata_files:
                        if not Path(metadata_file).is_absolute():
                            input_dir = (Path(input_file).parent).resolve()
                            metadata_file = input_dir / Path(metadata_file).name
                        self.load_rcs_metadatada(metadata_file)
                    self.main_window.mode_select_menu.set_options_enabled(False)
                    self.main_window.incident_wave_menu.set_options_enabled(False)
                    self.main_window.solver_setup_menu.set_options_enabled(False)

                    self.disable_options()
                else:
                    self.main_window.mode_select_menu.mode_state_changed()

            # pickup the last data, and populate the post proc windows
            rcs_objects = properties.radar_explorer.all_scene_actors["plotter"]
            if len(rcs_objects.values()) > 1:
                raise Exception("Not tested for multiple solutions")
            if not rcs_objects:
                self.ui.update_logger("Configuration loaded successfully")
            else:
                last_data = next(reversed(rcs_objects.values()), None)
                CommonWindowUtilsRCS.set_visible_post_proc(self, True, last_data)
                self.ui.update_logger("RCS data loaded successfully")

            self.ui.update_progress(100)
            self.is_loaded = True
            return True
        else:
            if not self.main_window.settings_menu.aedt_thread or (
                hasattr(self.main_window.settings_menu.aedt_thread, "aedt_launched")
                and not self.main_window.settings_menu.aedt_thread.aedt_launched
            ):
                msg = "AEDT not launched"
                self.ui.update_logger(msg)
                return False

            if self.main_window.backend_connected:
                if not self.aedt_toggle.isChecked():  # Load design
                    if not self.solved_toggle.isChecked():
                        selected_project = self.main_window.home_menu.project_combobox.currentText()
                        selected_design = self.main_window.home_menu.design_combobox.currentText()
                        setup = self.main_window.home_menu.setup_combobox.currentText()
                        sweep = self.main_window.home_menu.sweep_combobox.currentText()

                        be_properties = self.main_window.get_properties()
                        be_properties["active_design"] = selected_design
                        be_properties["active_project"] = selected_project
                        be_properties["setup"]["setup_name"] = setup
                        be_properties["setup"]["sweep_name"] = sweep
                        self.main_window.set_properties(be_properties)

                        excitation = self.main_window.home_menu.rcs_setup_combobox.currentText()
                        expression = self.main_window.home_menu.expression_combobox.currentText()

                        if expression == "RCS Theta":
                            expression = "ComplexMonostaticRCSTheta"
                        else:
                            expression = "ComplexMonostaticRCSPhi"
                        if excitation == "No Setup" or setup == "No Setup" or selected_design == "No Design":
                            self.ui.update_logger("Wrong selection")
                            self.ui.update_progress(100)
                            return False
                        metadata_file = self.ui.app.export_rcs(excitation, expression)
                        if not metadata_file:
                            self.ui.update_progress(100)
                            return False
                        self.plotter.rotation_active = False

                        self.load_rcs_metadatada(metadata_file)

                        self.is_independent = True

                        rcs_objects = properties.radar_explorer.all_scene_actors["plotter"]

                        last_data = next(reversed(rcs_objects.values()), None)
                        CommonWindowUtilsRCS.set_visible_post_proc(self, True, last_data)

                        self.ui.update_progress(100)
                        self.is_loaded = True
                        self.disable_options()
                        return True
                    else:
                        if (
                            self.duplicate_design_thread
                            and self.duplicate_design_thread.isRunning()
                            or self.main_window.backend_busy()
                        ):
                            msg = "Toolkit running"
                            self.ui.update_logger(msg)
                            self.main_window.logger.debug(msg)
                            return False

                        selected_project = self.main_window.home_menu.project_combobox.currentText()
                        selected_design = self.main_window.home_menu.design_combobox.currentText()

                        be_properties = self.main_window.get_properties()
                        be_properties["active_design"] = selected_design
                        be_properties["active_project"] = selected_project
                        self.main_window.set_properties(be_properties)

                        if selected_design == "No Design":
                            self.ui.update_logger("Wrong selection")
                            self.ui.update_progress(100)
                            return False

                        # Start a separate thread for the backend call
                        self.duplicate_design_thread = DuplicateDesignThread(app=self)

                        self.duplicate_design_thread.finished_signal.connect(self.duplicated_design_finished)

                        self.duplicate_design_thread.start()
                        self.ui.update_progress(50)
                        self.ui.update_logger("Duplicating design")
                        self.is_loaded = True
                        return True

                else:
                    if self.import_cad_thread and self.import_cad_thread.isRunning() or self.main_window.backend_busy():
                        msg = "Toolkit running"
                        self.ui.update_logger(msg)
                        self.main_window.logger.debug(msg)
                        return False

                    # Get material and origin
                    cad_file = Path(self.file.text())
                    material = self.material_combobox.currentText()
                    x = unit_converter_rcs(self.origin_x_textbox.text_full_precision(), "meter")
                    y = unit_converter_rcs(self.origin_y_textbox.text_full_precision(), "meter")
                    z = unit_converter_rcs(self.origin_z_textbox.text_full_precision(), "meter")

                    position = [x, y, z]

                    units = properties.radar_explorer.model_units

                    # Start a separate thread for the backend call
                    self.import_cad_thread = ImportCADThread(
                        app=self,
                        input_file=cad_file,
                        material=material,
                        position=position,
                        units=units
                    )

                    self.import_cad_thread.finished_signal.connect(self.import_cad_finished)

                    msg = "Importing CAD and inserting new design"
                    self.ui.update_logger(msg)
                    self.ui.update_progress(50)
                    self.import_cad_thread.start()
                    self.is_loaded = True
                    return True
            else:
                self.ui.update_logger("Backend not connected")
                self.ui.update_progress(100)
                return True

    def import_cad_finished(self):
        self.ui.update_progress(100)

        if self.import_cad_thread.metadata_file:
            self.disable_options()
            self.main_window.incident_wave_menu.set_options_enabled(True)
            self.main_window.solver_setup_menu.solve_button.setEnabled(True)
            be_properties = self.main_window.get_properties()
            self.design_combobox.blockSignals(True)
            self.design_combobox.clear()
            self.design_combobox.addItems([be_properties["active_design"]])
            self.design_combobox.setEnabled(False)
            self.ui.update_logger("CAD imported successfully")
            self.load_rcs_metadatada(self.import_cad_thread.metadata_file)
        else:
            self.ui.update_logger("CAD could not be imported")
            self.ui.update_progress(100)
            return False

    def duplicated_design_finished(self):
        self.ui.update_progress(100)
        if self.duplicate_design_thread.metadata_file:
            self.disable_options()
            self.main_window.solver_setup_menu.solve_button.setEnabled(True)
            self.ui.update_logger("Design duplicated successfully")
            self.load_rcs_metadatada(self.duplicate_design_thread.metadata_file)
            self.ui.update_progress(100)
        else:
            self.ui.update_logger("Design could not be imported")
            self.ui.update_progress(100)
            return False

    def load_rcs_metadatada(self, input_file):
        # Load RCS information
        rcs_object = self.ui.app.load_rcs_data_from_file(input_file)
        if not rcs_object:
            self.ui.update_logger("RCS not loaded")
            self.ui.update_progress(100)
            return False

        # Plot scene
        self.add_model_scene(rcs_object)

        # Save solution name
        solution_name = rcs_object.rcs_data.solution
        properties.radar_explorer.solution_names.append(solution_name)
        properties.radar_explorer.solution_names = list(set(properties.radar_explorer.solution_names))

        # Save results
        if solution_name not in properties.radar_explorer.all_scene_actors["plotter"]:
            properties.radar_explorer.all_scene_actors["plotter"][solution_name] = {}
            if "No solution" in self.main_window.incident_wave_menu.solution_selection_combobox.currentText():
                self.main_window.incident_wave_menu.solution_selection_combobox.clear()
            self.main_window.incident_wave_menu.solution_selection_combobox.addItem(solution_name)
        polarization = rcs_object.rcs_data.name
        properties.radar_explorer.all_scene_actors["plotter"][solution_name][polarization] = rcs_object

    def add_model_scene(self, rcs_object):
        imported_solutions = properties.radar_explorer.all_scene_actors["model"]

        # Clean plotter
        if "Ansys_scene" in imported_solutions.keys():  # pragma: no cover
            self.reset_scene()

        solution_name = rcs_object.rcs_data.solution

        polarization = "Unknown"
        if rcs_object.rcs_data.name in ["VV", "VH", "HV", "HH"]:
            polarization = rcs_object.rcs_data.name

        if solution_name not in properties.radar_explorer.all_scene_actors["model"]:
            self.rcs_object[solution_name] = {}
            properties.radar_explorer.all_scene_actors["model"][solution_name] = {}

        self.rcs_object[solution_name][polarization] = rcs_object

        # Get objects
        for model_name, model_data in rcs_object.all_scene_actors["model"].items():
            properties.radar_explorer.all_scene_actors["model"][solution_name][model_name] = model_data.custom_object

        # Plot scene
        self.plotter.plot_model_scene()
        self.plotter.plotter.view_isometric()

    # 3D Settings Column
    def model_3d_settings_setup(self):
        if self.model_settings_label is None:
            # Add icon
            spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.home_column_vertical_layout.addItem(spacer)

            layout_row_obj = QHBoxLayout()
            self.home_column_vertical_layout.addLayout(layout_row_obj)

            self.model_settings_label = QLabel("3D Settings")
            self.model_settings_label.setStyleSheet(
                f"font-size: {self.title_size}pt; color: {self.active_color};font-weight: bold;"
            )
            layout_row_obj.addWidget(self.model_settings_label)

            theme = self.main_window.ui.themes
            self.model_setting_icon = PyIconButton(
                icon_path=self.ui.images_load.icon_path("icon_settings.svg"),
                tooltip_text=None,
                width=40,
                height=40,
                radius=10,
                dark_one=theme["app_color"]["dark_one"],
                icon_color=theme["app_color"]["icon_color"],
                icon_color_hover=theme["app_color"]["icon_hover"],
                icon_color_pressed=theme["app_color"]["icon_active"],
                icon_color_active=theme["app_color"]["icon_active"],
                bg_color=theme["app_color"]["dark_one"],
                bg_color_hover=theme["app_color"]["dark_three"],
                bg_color_pressed=theme["app_color"]["pink"],
            )
            self.model_setting_icon.setMinimumHeight(40)
            layout_row_obj.addWidget(self.model_setting_icon)
            self.model_setting_icon.clicked.connect(lambda: self.model_3d_settings())

    def model_3d_settings(self):
        self.main_window.settings_menu.hide_widgets()

        if not self.model_loaded_tree:
            # Column
            layout = QVBoxLayout()

            # 3D Model title
            self.model_settings_column_label = QLabel("Model settings")
            self.model_settings_column_label.setStyleSheet(
                f"font-size: {self.title_size}pt; color: {self.active_color};font-weight: bold;"
            )
            layout.addWidget(self.model_settings_column_label)

            # Spacer
            spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Minimum)
            layout.addItem(spacer)

            # 3D Model table
            self.model_loaded_tree = QTreeWidget()
            self.model_loaded_tree.setHeaderLabels(["Solution", "Name", "Show", "Color", "Opacity"])
            self.model_loaded_tree.setObjectName("model_loaded_tree")

            table_style = (
                "QTreeWidget {{ background: {_bg_color}; color: {_active_color}; font-size: {"
                "_font_size}pt;}}"
                "QTreeWidget:item:selected {{background:  {_selection};}}"
                "QTreeWidget:item:hover {{background: {_hover};}}"
            )

            custom_style = table_style.format(
                _bg_color=self.app_color["combo_color"],
                _font_size=self.title_size,
                _active_color=self.active_color,
                _hover=self.app_color["combo_hover"],
                _selection=self.background_color,
            )

            self.model_loaded_tree.setStyleSheet(custom_style)

            header = self.model_loaded_tree.header()
            header.setStyleSheet(f"""
                                        QHeaderView::section {{
                                            background-color: {self.background_color};
                                            color: {self.active_color};
                                            font-size: {self.title_size}pt;
                                            padding: 2px;
                                        }}
                                    """)
            self.model_loaded_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            layout.addWidget(self.model_loaded_tree)

            # Spacer
            self.separator1 = self.ui.add_vertical_line(layout, [0, 20], [0, 20])

            # Post 3D title
            self.post_settings_column_label = QLabel("Plot settings")
            self.post_settings_column_label.setStyleSheet(
                f"font-size: {self.title_size}pt; color: {self.active_color};font-weight: bold;"
            )
            layout.addWidget(self.post_settings_column_label)

            # Spacer
            spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Minimum)
            layout.addItem(spacer)

            # Post Table
            self.post_3d_loaded_tree = QTreeWidget()
            self.post_3d_loaded_tree.setHeaderLabels(["Solution",
                                                      "Name",
                                                      "Show",
                                                      "Colormap",
                                                      "Opacity",
                                                      "Min Limit",
                                                      "Max Limit"])
            self.post_3d_loaded_tree.setObjectName(u"post_3d_loaded_tree")

            table_style = (
                "QTreeWidget {{ background: {_bg_color}; color: {_active_color}; font-size: {"
                "_font_size}pt;}}"
                "QTreeWidget:item:selected {{background:  {_selection};}}"
                "QTreeWidget:item:hover {{background: {_hover};}}"
            )

            custom_style = table_style.format(
                _bg_color=self.app_color["combo_color"],
                _font_size=self.title_size,
                _active_color=self.active_color,
                _hover=self.app_color["combo_hover"],
                _selection=self.background_color,
            )

            self.post_3d_loaded_tree.setStyleSheet(custom_style)

            header = self.post_3d_loaded_tree.header()
            header.setStyleSheet(f"""
                                    QHeaderView::section
                                    {{
                                    background-color: {self.background_color};
                                    color: {self.active_color};
                                    font-size: {self.title_size}pt;
                                    padding: 2px;
                                    }}
                                """)
            self.post_3d_loaded_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            layout.addWidget(self.post_3d_loaded_tree)

            row_returns = self.ui.add_n_buttons(
                layout,
                num_buttons=1,
                height=40,
                width=[180],
                text=["Delete plot"],
                font_size=self.main_window.properties.font["title_size"],
            )

            self.post_3d_delete_button_layout = row_returns[0]
            self.post_3d_delete_button = row_returns[1]
            self.post_3d_delete_button_layout.addWidget(self.post_3d_delete_button)
            self.post_3d_delete_button.clicked.connect(self.post_3d_delete_clicked)
            self.post_3d_delete_button.setEnabled(False)
            layout.setAlignment(Qt.AlignCenter)

            # Spacer
            self.separator3 = self.ui.add_vertical_line(layout, [0, 20], [0, 20])

            font_size = self.main_window.properties.font["title_size"]
            available_units = AVAILABLE_UNITS
            row_returns = self.ui.add_combobox(
                layout,
                height=40,
                width=[135, 180],
                label="Model units",
                combobox_list=available_units,
                font_size=font_size,
            )
            self.model_units_menu_layout = row_returns[0]
            self.model_units_menu_label = row_returns[1]
            self.model_unit_menu = row_returns[2]
            self.model_unit_menu.currentTextChanged.connect(lambda: self.change_model_units())

            # Spacer
            self.separator2 = self.ui.add_vertical_line(layout, [0, 20], [0, 20])

            font_size = self.main_window.properties.font["title_size"]
            categories = PROJECTION_CATEGORIES_LIST
            row_returns = self.ui.add_combobox(
                layout,
                height=40,
                width=[135, 180],
                label="Projection",
                combobox_list=categories,
                font_size=font_size,
            )
            self.projection_menu_layout = row_returns[0]
            self.projection_menu_label = row_returns[1]
            self.projection_menu = row_returns[2]
            self.projection_menu.currentTextChanged.connect(lambda: self.change_projection())

            self.main_window.ui.right_column.menus.settings_vertical_layout.addLayout(layout)

            self.right_column_visibility(True)

            self.main_window.ui.right_column.menus.settings_vertical_layout.addLayout(layout)

        else:
            self.right_column_visibility(True)

        self.main_window.post_2d_menu.right_column_visibility(False)

        # Populate trees
        self.populate_model_tree()
        self.populate_post_3d_tree()

        self.ui.set_right_column_menu("3D settings")
        self.ui.toggle_right_column()

    def populate_model_tree(self):
        # Populate tree
        self.model_loaded_tree.blockSignals(True)
        self.model_loaded_tree.clear()

        for scene_name, scene_models in properties.radar_explorer.all_scene_actors["model"].items():
            main_item = QTreeWidgetItem(self.model_loaded_tree, [scene_name, "", "", "", ""])

            for model_name, model in scene_models.items():
                item = QTreeWidgetItem(main_item, ["", model_name, "", "", ""])
                item._original_name = model_name

                # Create the combobox for show (True/False)
                combo_box_show = QComboBox()
                combo_box_show.addItems(["True", "False"])
                combo_box_show.setCurrentText(str(model.show))

                combo_box_style = """
                                    QComboBox {{
                                        border: none;
                                        padding: 10px;
                                        color: {_color};
                                        background-color: {_bg_color};
                                        selection-background-color: red;
                                        font-size: {_font_size}pt;
                                    }}
                                    QComboBox QAbstractItemView {{
                                        border: none;
                                        background-color: {_bg_color};
                                        color: {_color};
                                    }}
                                """
                custom_style = combo_box_style.format(
                    _color=self.app_color["text_foreground"],
                    _bg_color=self.app_color["combo_color"],
                    _font_size=self.main_window.properties.font["title_size"],
                )
                combo_box_show.setStyleSheet(custom_style)

                # Connect the combobox signal to a method
                combo_box_show.currentTextChanged.connect(
                    lambda text, scene_c=scene_name, it=item: self.on_combobox_show_changed(text,
                                                                                            scene_c,
                                                                                            it)
                )

                # Create the colormap text box
                colormap_edit = QLineEdit()
                # Set initial text
                colormap_edit.setText(str(model.color))

                line_edit_style = """
                                   QLineEdit {{
                                       border: none;
                                       padding: 10px;
                                       color: {_color};
                                       background-color: {_bg_color};
                                       font-size: {_font_size}pt;
                                   }}
                                   """
                colormap_edit.setStyleSheet(
                    line_edit_style.format(
                        _color=self.app_color["text_foreground"],
                        _bg_color=self.app_color["combo_color"],
                        _font_size=self.main_window.properties.font["title_size"],
                    )
                )

                # Connect the line_edit signal to a method when editing is finished
                colormap_edit.editingFinished.connect(
                    lambda scene=scene_name, model_c=model_name, le=colormap_edit: self.on_text_color_edit_finished(
                        scene, model_c, le
                    )
                )

                # Crete the line edit for opacity
                line_edit = QLineEdit()
                line_edit.setText(str(model.opacity))

                line_edit_style = """
                                    QLineEdit {{
                                        border: none;
                                        padding: 10px;
                                        color: {_color};
                                        background-color: {_bg_color};
                                        font-size: {_font_size}pt;
                                    }}
                                    """
                line_edit.setStyleSheet(
                    line_edit_style.format(
                        _color=self.app_color["text_foreground"],
                        _bg_color=self.app_color["combo_color"],
                        _font_size=self.main_window.properties.font["title_size"],
                    )
                )

                # Connect the line_edit signal to a method when editing is finished
                line_edit.editingFinished.connect(
                    lambda scene=scene_name, model_c=model_name, le=line_edit: self.on_text_edit_opacity_finished(
                        scene, model_c, le
                    )
                )

                # Add the combobox and spinbox as children to the item
                self.model_loaded_tree.setItemWidget(item, 2, combo_box_show)  # Show column
                self.model_loaded_tree.setItemWidget(item, 3, colormap_edit)  # Colormap column
                self.model_loaded_tree.setItemWidget(item, 4, line_edit)  # Opacity column

            self.model_loaded_tree.addTopLevelItem(main_item)

        self.model_loaded_tree.expandAll()
        self.model_loaded_tree.blockSignals(False)

    def populate_post_3d_tree(self):
        # Populate tree
        self.post_3d_loaded_tree.blockSignals(True)
        self.post_3d_loaded_tree.clear()

        solutions = {}
        for scene_name in properties.radar_explorer.all_scene_actors['model']:
            item = QTreeWidgetItem(self.post_3d_loaded_tree, [scene_name, "", "", "", "", "", ""])
            solutions[scene_name] = item

        for scene_name, scene_models in properties.radar_explorer.all_scene_actors["results"].items():
            if properties.radar_explorer.reports.get("Results", None) and scene_name in list(
                properties.radar_explorer.reports["Results"].keys()
            ):
                continue
            self.post_3d_delete_button.setEnabled(True)
            if scene_name in solutions:
                main_item = solutions[scene_name]
            else:
                main_item = QTreeWidgetItem(self.post_3d_loaded_tree, [scene_name, "", "", "", "", "", ""])

            for model_name, model in scene_models.items():
                if not hasattr(model, "custom_object"):
                    continue
                self.populate_row(main_item, scene_name, model_name, model.custom_object)

            self.post_3d_loaded_tree.addTopLevelItem(main_item)

        self.post_3d_loaded_tree.expandAll()
        self.post_3d_loaded_tree.blockSignals(False)

    def populate_row(self, main_item, scene_name, model_name, model):
        item = QTreeWidgetItem(main_item, ["", model_name, "", "", "", "", ""])
        item._original_name = model_name
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        self.post_3d_loaded_tree.itemChanged.connect(self.on_item_name_changed)

        # Create the combobox for show (True/False)
        combo_box_show = QComboBox()
        combo_box_show.addItems(["True", "False"])
        combo_box_show.setCurrentText(str(model.show))

        combo_box_style = """
                                            QComboBox {{
                                                border: none;
                                                padding: 10px;
                                                color: {_color};
                                                background-color: {_bg_color};
                                                selection-background-color: red;
                                                font-size: {_font_size}pt;
                                            }}
                                            QComboBox QAbstractItemView {{
                                                border: none;
                                                background-color: {_bg_color};
                                                color: {_color};
                                            }}
                                        """
        custom_style = combo_box_style.format(
            _color=self.app_color["text_foreground"],
            _bg_color=self.app_color["combo_color"],
            _font_size=self.main_window.properties.font["title_size"],
        )
        combo_box_show.setStyleSheet(custom_style)

        # Connect the combobox signal to a method
        combo_box_show.currentTextChanged.connect(
            lambda text, scene_c=scene_name, it=item: self.on_combobox_show_changed(text, scene_c, it)
        )

        # Create the combobox for colormap
        combo_box_colormap = QComboBox()
        # Use all colormaps supported by matplotlib
        colormap_list = list(colormaps)
        combo_box_colormap.addItems(colormap_list)
        # Optionally, set current colormap if model has one, else default
        if hasattr(model, "color_map") and model.color_map in colormap_list:
            combo_box_colormap.setCurrentText(model.color_map)
        else:
            combo_box_colormap.setCurrentText("jet")

        combo_box_colormap.setStyleSheet(custom_style)

        # Connect the combobox signal to a method
        combo_box_colormap.currentTextChanged.connect(
            lambda text, scene_c=scene_name, it=item: self.on_combobox_colormap_changed(text,
                                                                                        scene_c,
                                                                                        it)
        )

        # Crete the line edit for opacity
        line_edit = QLineEdit()
        line_edit.setText(str(model.opacity))  # Set initial text

        line_edit_style = """
                            QLineEdit {{
                                border: none;
                                padding: 10px;
                                color: {_color};
                                background-color: {_bg_color};
                                font-size: {_font_size}pt;
                            }}
                            """
        line_edit.setStyleSheet(
            line_edit_style.format(
                _color=self.app_color["text_foreground"],
                _bg_color=self.app_color["combo_color"],
                _font_size=self.main_window.properties.font["title_size"],
            )
        )

        # Connect the line_edit signal to a method when editing is finished
        line_edit.editingFinished.connect(
            lambda scene=scene_name, it=item, le=line_edit: self.on_text_edit_3d_post_finished(scene,
                                                                                               it,
                                                                                               le)
        )

        # Crete the line edit for min value
        min_value = QLineEdit()
        if model.clim is not None:
            min_value.setText(str(round(model.clim[0], self.ui.app.properties.radar_explorer.precision)))
        else:
            min_value.setText("")
            min_value.setReadOnly(True)

        min_value_style = """
                            QLineEdit {{
                                border: none;
                                padding: 10px;
                                color: {_color};
                                background-color: {_bg_color};
                                font-size: {_font_size}pt;
                            }}
                            """
        min_value.setStyleSheet(min_value_style.format(
            _color=self.app_color["text_foreground"],
            _bg_color=self.app_color["combo_color"],
            _font_size=self.main_window.properties.font["title_size"]
        ))

        # Crete the line edit for max value
        max_value = QLineEdit()
        if model.clim is not None:
            max_value.setText(str(round(model.clim[1], self.ui.app.properties.radar_explorer.precision)))
        else:
            max_value.setText("")
            max_value.setReadOnly(True)

        max_value_style = """
                            QLineEdit {{
                                border: none;
                                padding: 10px;
                                color: {_color};
                                background-color: {_bg_color};
                                font-size: {_font_size}pt;
                            }}
                            """
        max_value.setStyleSheet(max_value_style.format(
            _color=self.app_color["text_foreground"],
            _bg_color=self.app_color["combo_color"],
            _font_size=self.main_window.properties.font["title_size"]
        ))

        if model.clim is not None:

            # Connect the min_value signal to a method when editing is finished
            min_value.editingFinished.connect(
                lambda scene=scene_name, it=item, minv=min_value, maxv=max_value:
                self.on_text_edit_min_max_post_finished(scene,
                                                        it,
                                                        minv,
                                                        maxv,
                                                        )
            )

            # Connect the max_value signal to a method when editing is finished
            max_value.editingFinished.connect(
                lambda scene=scene_name, it=item, minv=min_value, maxv=max_value:
                self.on_text_edit_min_max_post_finished(scene,
                                                        it,
                                                        minv,
                                                        maxv,
                                                        )
            )

        # Add the combobox and spinbox as children to the item
        self.post_3d_loaded_tree.setItemWidget(item, 2, combo_box_show)  # Show column
        self.post_3d_loaded_tree.setItemWidget(item, 3, combo_box_colormap)  # Colormap column
        self.post_3d_loaded_tree.setItemWidget(item, 4, line_edit)  # Opacity column
        self.post_3d_loaded_tree.setItemWidget(item, 5, min_value)  # Min value column
        self.post_3d_loaded_tree.setItemWidget(item, 6, max_value)  # Min value column

    def on_item_name_changed(self, item, column):
        if column != 1:
            return

        new_name = item.text(1)

        # Check if name is duplicated
        for _, scenario in properties.radar_explorer.all_scene_actors["results"].items():
            for result in scenario.keys():
                if result == new_name:
                    self.post_3d_loaded_tree.blockSignals(True)
                    item.setText(1, item._original_name)
                    # self.ui.update_logger(f"Duplicated result name.") # It is called 2 times
                    self.post_3d_loaded_tree.itemChanged.connect(self.on_item_name_changed)
                    self.post_3d_loaded_tree.blockSignals(False)
                    return

        for scenario_name, scenario in properties.radar_explorer.all_scene_actors["results"].items():
            for result in scenario.keys():
                if result == item._original_name:
                    result_dict = properties.radar_explorer.all_scene_actors["results"][scenario_name]
                    result_dict[new_name] = result_dict.pop(result)
                    item._original_name = new_name
                    self.plotter.plot_model_scene()
                    break

    def on_combobox_show_changed(self, value, scene_name, item):
        show = False
        model = None
        name = item._original_name

        if value == "True":
            show = True

        if scene_name in properties.radar_explorer.all_scene_actors["model"]:
            if name in properties.radar_explorer.all_scene_actors["model"][scene_name]:
                model = properties.radar_explorer.all_scene_actors["model"][scene_name][name]
                model.show = show

        if model is None and scene_name in properties.radar_explorer.all_scene_actors["results"]:
            if name in properties.radar_explorer.all_scene_actors["results"][scene_name]:
                model = properties.radar_explorer.all_scene_actors["results"][scene_name][name]
                model.custom_object.show = show

        self.plotter.plot_model_scene()

    def on_combobox_colormap_changed(self, value, scene_name, item):
        model = None
        name = item._original_name
        if scene_name in properties.radar_explorer.all_scene_actors["results"]:
            if name in properties.radar_explorer.all_scene_actors["results"][scene_name]:
                model = properties.radar_explorer.all_scene_actors["results"][scene_name][name].custom_object
        if model:
            model.color_map = value
        self.plotter.plot_model_scene()

    def on_text_edit_opacity_finished(self, name, model_name, line_edit):
        model = None
        if model_name in properties.radar_explorer.all_scene_actors["model"][name]:
            model = properties.radar_explorer.all_scene_actors["model"][name][model_name]
        elif model_name in properties.radar_explorer.all_scene_actors["results"][name]:
            model = properties.radar_explorer.all_scene_actors["results"][name][model_name].custom_object
        if model:
            text = line_edit.text()
            if "[" in text and "]" in text:
                model.opacity = ast.literal_eval(text)
            else:
                try:
                    model.opacity = float(text)
                except ValueError:
                    model.opacity = text

        self.plotter.plot_model_scene()

    def on_text_color_edit_finished(self, name, model_name, line_edit):
        model = None
        if model_name in properties.radar_explorer.all_scene_actors["model"][name]:
            model = properties.radar_explorer.all_scene_actors["model"][name][model_name]
        elif model_name in properties.radar_explorer.all_scene_actors["results"][name]:
            model = properties.radar_explorer.all_scene_actors["results"][name][model_name].custom_object
        if model:
            text = line_edit.text()
            try:
                if "[" in text and "]" in text:
                    model.color = ast.literal_eval(text)
                elif text != "":
                    model.color = line_edit.text()
            except SyntaxError:
                self.ui.update_logger(f"Wrong color: {text}. Using red by default")
                model.color = "red"

        self.plotter.plot_model_scene()

    def on_text_edit_3d_post_finished(self, scene_name, item, line_edit):
        model = None
        name = item._original_name
        if scene_name in properties.radar_explorer.all_scene_actors["results"]:
            if name in properties.radar_explorer.all_scene_actors["results"][scene_name]:
                model = properties.radar_explorer.all_scene_actors["results"][scene_name][name].custom_object
        if model:
            text = line_edit.text()
            if "[" in text and "]" in text:
                model.opacity = ast.literal_eval(text)
            else:
                try:
                    model.opacity = float(text)
                except ValueError:
                    model.opacity = text

        self.plotter.plot_model_scene()

    def on_text_edit_min_max_post_finished(self, scene_name, item, min_value, max_value):
        model = None
        name = item._original_name
        if scene_name in properties.radar_explorer.all_scene_actors["results"]:
            if name in properties.radar_explorer.all_scene_actors["results"][scene_name]:
                model = properties.radar_explorer.all_scene_actors["results"][scene_name][name].custom_object
        if model:
            min_value_str = min_value.text()
            if min_value_str == "default":
                min_value_str = str(round(model.default_clim[0], self.ui.app.properties.radar_explorer.precision))

            max_value_str = max_value.text()
            if max_value_str == "default":
                max_value_str = str(round(model.default_clim[1], self.ui.app.properties.radar_explorer.precision))

            if float(max_value_str) < float(min_value_str):
                # Apply default
                max_value_str = str(round(model.default_clim[1], self.ui.app.properties.radar_explorer.precision))
                min_value_str = str(round(model.default_clim[0], self.ui.app.properties.radar_explorer.precision))
                self.ui.update_logger(f"Maximum limit must be greater than minimun limit. "
                                      f"Using default: {min_value_str}, {max_value_str}.")

            model.clim = (float(min_value_str), float(max_value_str))

            min_value.setText(min_value_str)
            max_value.setText(max_value_str)

            if model.plot_type == "iso-surface":
                actor = model.default_mesh
                contour_values = np.linspace(float(min_value_str),
                                             float(max_value_str),
                                             properties.radar_explorer.num_contours)
                new_contours = actor.contour(isosurfaces=contour_values)
                model.mesh = new_contours

        self.plotter.plot_model_scene()

    def post_3d_delete_clicked(self):
        for i in range(self.post_3d_loaded_tree.topLevelItemCount()):
            main_item = self.post_3d_loaded_tree.topLevelItem(i)
            # main_state = main_item.checkState(2) == Qt.Checked
            result_name = main_item.text(0)
            for j in range(main_item.childCount()):
                child_item = main_item.child(j)
                child_state = child_item.isSelected()
                if child_state:
                    child_name = child_item.text(1)
                    if (
                        result_name in properties.radar_explorer.all_scene_actors["results"]
                        and child_name in properties.radar_explorer.all_scene_actors["results"][result_name]
                    ):
                        del properties.radar_explorer.all_scene_actors["results"][result_name][child_name]
                        self.ui.update_logger(f"Delete {child_name}")

        self.plotter.plot_model_scene()
        self.populate_post_3d_tree()

    def right_column_visibility(self, visible=False):
        if self.model_loaded_tree:
            self.model_loaded_tree.setVisible(visible)
            self.projection_menu.setVisible(visible)
            self.projection_menu_label.setVisible(visible)
            self.model_settings_column_label.setVisible(visible)
            self.model_loaded_tree.setVisible(visible)
            self.separator1.setVisible(visible)
            self.post_settings_column_label.setVisible(visible)
            self.post_3d_loaded_tree.setVisible(visible)
            self.post_3d_delete_button.setVisible(visible)
            if self.is_loaded:
                self.separator2.setVisible(False)
                self.model_unit_menu.setVisible(False)
                self.model_units_menu_label.setVisible(False)
            else:
                self.separator2.setVisible(visible)
                self.model_unit_menu.setVisible(visible)
                self.model_units_menu_label.setVisible(visible)

    def reset_scene(self):
        self.plotter.clear_window_actors()
        properties.radar_explorer.all_scene_actors["model"] = {}
        properties.radar_explorer.all_scene_actors["plotter"] = {}

    def update_project(self):
        self.project_combobox.blockSignals(True)
        self.material_combobox.blockSignals(True)
        project_list = self.main_window.get_aedt_data()
        self.main_window.home_menu.project_combobox.setEnabled(True)
        self.main_window.home_menu.project_combobox.clear()
        self.main_window.home_menu.project_combobox.addItems(project_list)

        self.material_combobox.clear()
        materials = self.main_window.get_materials()
        self.material_combobox.addItems(materials)

        self.project_combobox.blockSignals(False)
        self.material_combobox.blockSignals(False)
        return project_list

    def update_design(self):
        self.load_rcs_button.setEnabled(True)
        self.design_combobox.blockSignals(True)
        design_list = self.main_window.update_design_names(self.project_combobox.currentText())

        selected_design = self.design_combobox.currentText()

        self.main_window.home_menu.design_combobox.clear()
        self.main_window.home_menu.design_combobox.addItems(design_list)

        setup_index = 0
        sweep_index = 0
        plane_wave_index = 0

        if design_list and selected_design == "No Design":
            self.design_combobox.setCurrentIndex(0)
        if selected_design != "No Design":
            if selected_design not in design_list:
                selected_design = design_list[0]
            new_property = {"active_design": selected_design}
            self.main_window.set_properties(new_property)
            design_index = self.design_combobox.findText(selected_design)
            self.design_combobox.setCurrentIndex(design_index)
            # self.update_setup()
            # self.update_rcs_setup()

        self.setup_combobox.blockSignals(True)
        setups = self.ui.app.get_setups()
        self.main_window.home_menu.setup_combobox.clear()
        self.main_window.home_menu.setup_combobox.addItems(setups)
        self.setup_combobox.setCurrentIndex(setup_index)
        active_setup = self.setup_combobox.currentText()
        self.main_window.set_properties({"setup_name": active_setup})

        self.sweep_combobox.blockSignals(True)
        sweeps = self.ui.app.get_sweeps()
        self.main_window.home_menu.sweep_combobox.clear()
        self.main_window.home_menu.sweep_combobox.addItems(sweeps)
        self.sweep_combobox.setCurrentIndex(sweep_index)

        self.rcs_setup_combobox.blockSignals(True)
        plane_waves = self.ui.app.get_plane_waves()
        self.main_window.home_menu.rcs_setup_combobox.clear()
        self.main_window.home_menu.rcs_setup_combobox.addItems(plane_waves)
        self.rcs_setup_combobox.setCurrentIndex(plane_wave_index)

        self.rcs_setup_combobox.setEnabled(True)
        self.setup_combobox.setEnabled(True)
        self.sweep_combobox.setEnabled(True)
        self.design_combobox.setEnabled(True)
        self.setup_combobox.blockSignals(False)
        self.sweep_combobox.blockSignals(False)
        self.design_combobox.blockSignals(False)

    def update_setup(self):
        sweep_index = 0
        self.load_rcs_button.setEnabled(True)
        self.design_combobox.blockSignals(True)
        self.setup_combobox.blockSignals(True)
 
        active_setup = self.setup_combobox.currentText()
        self.main_window.set_properties({"setup_name": active_setup})

        self.sweep_combobox.blockSignals(True)
        sweeps = self.ui.app.get_sweeps()
        self.main_window.home_menu.sweep_combobox.clear()
        self.main_window.home_menu.sweep_combobox.addItems(sweeps)
        self.sweep_combobox.setCurrentIndex(sweep_index)

        self.rcs_setup_combobox.setEnabled(True)
        self.setup_combobox.setEnabled(True)
        self.sweep_combobox.setEnabled(True)
        self.setup_combobox.blockSignals(False)
        self.sweep_combobox.blockSignals(False)
        self.design_combobox.blockSignals(False)

    def initialize_plotter(self):
        self.plotter.add_to_window(self.class_name, self.home_layout)

    def disable_options(self):
        self.load_rcs_button.setEnabled(False)

        # Toggle

        # Import geometry

        # Browser
        self.browse.setEnabled(False)
        self.file.setEnabled(False)

        self.material_combobox.setEnabled(False)
        self.origin_x_textbox.setEnabled(False)
        self.origin_y_textbox.setEnabled(False)
        self.origin_z_textbox.setEnabled(False)

        # Load design

        # Project combo box
        self.project_combobox.setEnabled(False)
        self.design_combobox.setEnabled(False)
        self.rcs_setup_combobox.setEnabled(False)
        self.setup_combobox.setEnabled(False)
        self.sweep_combobox.setEnabled(False)
        self.expression_combobox.setEnabled(False)

    def __show_layout_widgets(self, layout, show=True):
        # Hide all widgets in the layout
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if isinstance(item, QHBoxLayout):
                self.__show_layout_widgets(item, show)
            if item.widget():
                if show:
                    item.widget().show()
                else:
                    item.widget().hide()

    # Column setup
    def __setup_toggle(self):
        row_returns = self.ui.add_toggle(
            self.file_mode_layout,
            height=30,
            width=[135, 120, 135],
            label=["File Mode", "AEDT Mode"],
            font_size=self.title_size,
            bg_color=self.app_color["label_off"],
            active_color=self.app_color["label_on"],
        )
        self.ui.left_column.menus.aedt_mode_select_row = row_returns[0]
        self.file_mode_label = row_returns[1]
        self.toggle = row_returns[2]
        self.aedt_mode_label = row_returns[3]

    def __aedt_setup_toggle(self):
        row_returns = self.ui.add_toggle(
            self.aedt_toggle_layout,
            height=30,
            width=[135, 120, 135],
            label=["Load design", "Import geometry"],
            font_size=self.title_size,
            bg_color=self.app_color["label_off"],
            active_color=self.app_color["label_on"],
        )
        self.load_design_select_row = row_returns[0]
        self.load_design_label = row_returns[1]
        self.aedt_toggle = row_returns[2]
        self.import_geometry_label = row_returns[3]

        self.__show_layout_widgets(self.load_design_select_row, False)

    def __open_file(self):
        row_returns = self.ui.add_icon_button(
            self.home_column_vertical_layout,
            icon=self.ui.images_load.icon_path("icon_folder_open.svg"),
            height=40,
            width=[40, 250],
            text="Browse...",
        )

        self.browse_file_group = row_returns[0]
        self.browse = row_returns[1]
        self.file = row_returns[2]

        self.spacer1 = QSpacerItem(0, 0)
        self.home_column_vertical_layout.addItem(self.spacer1)

        # self.spacer1.changeSize(0, 0)

        # Material

        row_returns = self.ui.add_combobox(
            self.aedt_mode_layout,
            height=40,
            width=[135, 180],
            label="Material",
            combobox_list=["pec"],
            font_size=self.combo_size,
        )

        self.material_widget = row_returns[0]
        self.material_label = row_returns[1]
        self.material_combobox = row_returns[2]

        self.spacer2 = QSpacerItem(0, 0)
        self.aedt_mode_layout.addItem(self.spacer2)

        self.__show_layout_widgets(self.material_widget, False)

        # Position
        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.aedt_mode_layout,
            height=40,
            width=[135, 180],
            label="Origin X",
            value=0.0,
            unit="m",
            font_size=self.combo_size,
        )

        self.origin_x_widget = row_returns[0]
        self.origin_x_label = row_returns[1]
        self.origin_x_textbox = row_returns[2]

        self.spacer3 = QSpacerItem(0, 0)
        self.aedt_mode_layout.addItem(self.spacer3)

        self.__show_layout_widgets(self.origin_x_widget, False)
        # self.spacer3.changeSize(0, 0)

        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.aedt_mode_layout,
            height=40,
            width=[135, 180],
            label="Origin Y",
            value=0.0,
            unit="m",
            font_size=self.combo_size,
        )

        self.origin_y_widget = row_returns[0]
        self.origin_y_label = row_returns[1]
        self.origin_y_textbox = row_returns[2]

        self.spacer4 = QSpacerItem(0, 0)
        # self.spacer4.changeSize(0, 0)

        self.__show_layout_widgets(self.origin_y_widget, False)
        self.aedt_mode_layout.addItem(self.spacer4)

        row_returns = self.rcs_utils.add_textbox_prec_unit(
            layout=self.aedt_mode_layout,
            height=40,
            width=[135, 180],
            label="Origin Z",
            value=0.0,
            unit="m",
            font_size=self.combo_size,
        )

        self.origin_z_widget = row_returns[0]
        self.origin_z_label = row_returns[1]
        self.origin_z_textbox = row_returns[2]

        self.spacer5 = QSpacerItem(0, 0)
        self.aedt_mode_layout.addItem(self.spacer5)
        self.__show_layout_widgets(self.origin_z_widget, False)
        # self.spacer5.changeSize(0, 0)

    def __setup_aedt_comboboxes(self):
        row_returns = self.ui.add_toggle(
            self.aedt_mode_layout,
            height=30,
            width=[135, 120, 135],
            label=["Get solution", "New solution"],
            font_size=self.title_size,
            bg_color=self.app_color["label_off"],
            active_color=self.app_color["label_on"],
        )
        self.solution_select_row = row_returns[0]
        self.get_solution_label = row_returns[1]
        self.solved_toggle = row_returns[2]
        self.new_solution_label = row_returns[3]
        self.solved_toggle.stateChanged.connect(self.solved_toggle_state_changed)

        spacer = QSpacerItem(0, 10)
        self.aedt_mode_layout.addItem(spacer)

        row_returns = self.ui.add_combobox(
            self.aedt_mode_layout,
            height=40,
            width=[135, 180],
            label="Project",
            combobox_list=["No Project"],
            font_size=self.combo_size,
        )

        self.project_combo_widget = row_returns[0]
        self.project_label = row_returns[1]
        self.project_combobox = row_returns[2]
        self.project_combobox.currentIndexChanged.connect(lambda: self.update_design())
        self.project_combobox.setEnabled(False)
        self.__show_layout_widgets(self.project_combo_widget, False)

        spacer = QSpacerItem(0, 0)
        self.aedt_mode_layout.addItem(spacer)

        row_returns = self.ui.add_combobox(
            self.aedt_mode_layout,
            height=40,
            width=[135, 180],
            label="Design",
            combobox_list=["No Design"],
            font_size=self.combo_size,
        )

        self.design_combo_widget = row_returns[0]
        self.design = row_returns[1]
        self.design_combobox = row_returns[2]
        self.design_combobox.currentIndexChanged.connect(lambda: self.update_design())
        self.design_combobox.setEnabled(False)
        self.__show_layout_widgets(self.design_combo_widget, False)

        row_returns = self.ui.add_combobox(
            self.aedt_mode_layout,
            height=40,
            width=[135, 180],
            label="RCS",
            combobox_list=["No Setup"],
            font_size=self.combo_size,
        )

        self.rcs_setup_combo_widget = row_returns[0]
        self.rcs_setup = row_returns[1]
        self.rcs_setup_combobox = row_returns[2]
        self.rcs_setup_combobox.setEnabled(False)
        self.__show_layout_widgets(self.rcs_setup_combo_widget, False)

        row_returns = self.ui.add_combobox(
            self.aedt_mode_layout,
            height=40,
            width=[135, 180],
            label="Setup",
            combobox_list=["No Setup"],
            font_size=self.combo_size,
        )

        self.setup_combo_widget = row_returns[0]
        self.setup = row_returns[1]
        self.setup_combobox = row_returns[2]
        self.setup_combobox.currentIndexChanged.connect(lambda: self.update_setup())
        self.setup_combobox.setEnabled(False)
        self.__show_layout_widgets(self.setup_combo_widget, False)

        row_returns = self.ui.add_combobox(
            self.aedt_mode_layout,
            height=40,
            width=[135, 180],
            label="Sweep",
            combobox_list=["No Sweep"],
            font_size=self.combo_size,
        )

        self.sweep_combo_widget = row_returns[0]
        self.sweep = row_returns[1]
        self.sweep_combobox = row_returns[2]
        self.sweep_combobox.setEnabled(False)
        self.__show_layout_widgets(self.sweep_combo_widget, False)

        row_returns = self.ui.add_combobox(
            self.aedt_mode_layout,
            height=40,
            width=[135, 180],
            label="Data",
            combobox_list=["No Data"],
            font_size=self.combo_size,
        )

        self.expression_combo_widget = row_returns[0]
        self.expression = row_returns[1]
        self.expression_combobox = row_returns[2]
        self.main_window.home_menu.expression_combobox.clear()
        self.main_window.home_menu.expression_combobox.addItems(["RCS Theta", "RCS Phi"])
        self.__show_layout_widgets(self.expression_combo_widget, False)

        spacer = QSpacerItem(0, 0)
        self.aedt_mode_layout.addItem(spacer)

        self.__show_layout_widgets(self.solution_select_row, False)

    def change_projection(self):
        selected_projection = self.projection_menu.currentText()
        if selected_projection == "Orthographic":
            self.plotter.plotter.enable_parallel_projection()
            properties.radar_explorer.all_scene_actors["plotter"]["parallel"] = True
        else:
            self.plotter.plotter.disable_parallel_projection()
            properties.radar_explorer.all_scene_actors["plotter"]["parallel"] = False

    def change_model_units(self):
        selected_units = self.model_unit_menu.currentText()
        properties.radar_explorer.model_units = selected_units
