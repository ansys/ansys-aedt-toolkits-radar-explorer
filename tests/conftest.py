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

"""Common conftest."""

from pathlib import Path
import shutil
from typing import List

import pytest

UI_TESTS_PREFIX = "tests/ui"
VISUALIZATION_TESTS_PREFIX = "tests/backend/tests_visualization"


@pytest.fixture(scope="session")
def common_temp_dir(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("test_radar_toolkit_workflows", numbered=True)
    src_folder = Path(__file__).parent / "input_data"
    shutil.copytree(src_folder, Path(tmp_dir) / "input_data")

    yield tmp_dir


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    """Apply marker on tests."""
    for item in items:
        # Mark unit, integration and system tests
        if item.nodeid.startswith(UI_TESTS_PREFIX):
            item.add_marker(pytest.mark.ui)
        elif item.nodeid.startswith(VISUALIZATION_TESTS_PREFIX):
            item.add_marker(pytest.mark.radar_visualization)
