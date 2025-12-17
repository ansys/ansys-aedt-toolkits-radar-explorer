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

from unittest.mock import patch

import pytest

from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSData

FILE_PATH = "dummy.json"
ERROR_MESSAGE = "JSON file does not exist."


@patch("pathlib.Path.is_file", return_value=False)
def test_failure_with_non_existing_file(mock_is_file):
    with pytest.raises(FileNotFoundError, match="JSON file does not exist."):
        MonostaticRCSData(input_file=FILE_PATH)
