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
import sys
import tempfile

# isort: off

from ansys.aedt.toolkits.radar_explorer.backend.api import ToolkitBackend

from ansys.aedt.toolkits.common.backend.multithreading_server import MultithreadingServer
from ansys.aedt.toolkits.common.backend.rest_api import app
from ansys.aedt.toolkits.common.backend.rest_api import jsonify
from ansys.aedt.toolkits.common.backend.rest_api import logger

from flask import request

# isort: on

toolkit_api = ToolkitBackend()

if len(sys.argv) == 3:  # pragma: no cover
    toolkit_api.properties.url = sys.argv[1]
    toolkit_api.properties.port = int(sys.argv[2])


@app.route("/export_rcs", methods=["GET"])
def export_rcs():
    logger.info("[GET] rcs_results (Get monostatic RCS data)")

    body = request.json

    # Default values
    default_values = {
        "excitation": None,
        "expression": None,
        "encode": True,
    }

    # Extract values from the request body
    params = {key: body.get(key, default_values[key]) for key in default_values}

    response = toolkit_api.export_rcs(**params)

    if response:
        return jsonify(str(response)), 200
    else:  # pragma: no cover
        return jsonify("Failed to get results."), 500


@app.route("/get_setups", methods=["GET"])
def get_setups():
    logger.info("[GET] setups (Get solved setups.)")
    return toolkit_api.get_setups()


@app.route("/get_plane_waves", methods=["GET"])
def get_plane_waves():
    logger.info("[GET] plane waves (Get plane wave setups.)")
    return toolkit_api.get_plane_waves()


@app.route("/duplicate_sbr_design", methods=["POST"])
def duplicate_sbr_design_route():
    # Endpoint to duplicate an existing SBR+ design.
    # Expected json payload:
    # {"name": "new_design_name"}
    data = request.get_json()
    name = data.get("name", None)
    try:
        # Initialize API and call duplicate function
        design_name = toolkit_api.duplicate_sbr_design(name)
        if design_name:
            return jsonify({"status": "success", "design_name": design_name}), 200
        else:  # pragma: no cover
            return jsonify({"status": "error", "message": "Failed to duplicate design."}), 500
    except Exception as e:  # pragma: no cover
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/generate_3d_component", methods=["GET"])
def generate_3d_component():
    logger.info("[GET] generate_3d_component (Generate 3D component.)")
    component_file = toolkit_api.generate_3d_component()
    if component_file:
        return jsonify(str(component_file)), 200
    else:  # pragma: no cover
        return jsonify("Fail to get results"), 500


@app.route("/insert_sbr_design", methods=["GET"])
def insert_sbr_design():
    logger.info("[GET] insert_sbr_design (Get monostatic RCS data.)")

    body = request.json

    # Default values
    default_values = {
        "input_file": None,
        "name": None,
    }

    # Extract values from the request body
    params = {key: body.get(key, default_values[key]) for key in default_values}

    response = toolkit_api.insert_sbr_design(**params)

    if response:
        return jsonify(str(response)), 200
    else:  # pragma: no cover
        return jsonify("Fail to get results."), 500


@app.route("/insert_cad", methods=["PUT"])
def insert_cad():
    logger.info("[PUT] insert_cad (Insert CAD model in HFSS.)")

    body = request.json

    input_file = body["input_file"]
    material = body["material"]
    position = body["position"]
    extension = body["extension"]
    units = body["units"]

    # Decode
    if not Path(input_file).is_file():
        temp_folder = tempfile.mkdtemp()
        encoded_data_bytes = bytes(input_file, "utf-8")
        decoded_data = base64.b64decode(encoded_data_bytes)
        file_name = f"rcs_object{extension}"
        file_path = Path(temp_folder) / file_name
        with file_path.open("wb") as f:
            f.write(decoded_data)
        input_file = file_path

    toolkit_api.properties.cad.input_file = [input_file]
    toolkit_api.properties.cad.material = [material]
    toolkit_api.properties.cad.position = [position]
    toolkit_api.properties.cad.model_units = units

    response = toolkit_api.insert_cad_sbr(name="rcs_scenario")

    if response:
        return jsonify(str(response)), 200
    else:  # pragma: no cover
        return jsonify("Failed to get results."), 500


@app.route("/add_plane_wave", methods=["GET"])
def add_plane_wave():
    logger.info("[GET] add_plane_wave (Add plane wave.)")
    v_plane_wave = toolkit_api.add_plane_wave(name="IncWaveVpol", polarization="Vertical")
    h_plane_wave = toolkit_api.add_plane_wave(name="IncWaveHpol", polarization="Horizontal")
    if v_plane_wave and h_plane_wave:
        return jsonify([v_plane_wave, h_plane_wave]), 200
    else:  # pragma: no cover
        return jsonify("Failed to create setup."), 500


@app.route("/create_setup", methods=["GET"])
def create_setup():
    logger.info("[GET] create_setup (Create setup.)")
    setup_name = toolkit_api.add_setup(name="rcs_setup")
    if setup_name:
        return jsonify(str(setup_name)), 200
    else:  # pragma: no cover
        return jsonify("Failed to create setup."), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    logger.info("[POST] /analyze (Analyze AEDT project in batch.)")

    response = toolkit_api.analyze()
    if response:
        return jsonify("AEDT design analysis has finished."), 200
    else:  # pragma: no cover
        return jsonify("Failed to launch design."), 500


@app.route("/get_materials", methods=["GET"])
def get_materials():
    logger.info("[GET] available materials (Get materials.)")
    return toolkit_api.get_materials()


@app.route("/get_sweeps", methods=["GET"])
def get_sweeps():
    logger.info("[GET] available sweeps (Get sweeps.)")
    return toolkit_api.get_sweeps()


def run_backend(port=0):
    """Run the server."""
    app.debug = toolkit_api.properties.debug
    server = MultithreadingServer()
    if port == 0:  # pragma: no cover
        port = toolkit_api.properties.port
    server.run(host=toolkit_api.properties.url, port=port, app=app)


if __name__ == "__main__":  # pragma: no cover
    run_backend()
