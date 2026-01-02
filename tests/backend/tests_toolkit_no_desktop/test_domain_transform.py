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

import numpy as np
import pytest

from ansys.aedt.core.generic.constants import SpeedOfLight
from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.domain_transforms import DomainTransforms
from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.utils import split_num_units
from ansys.aedt.toolkits.radar_explorer.backend.rcs_utils.utils import unit_converter_rcs

pytestmark = [pytest.mark.domain_transforms]


class TestDomainTransforms:
    @pytest.fixture
    def setup_data(self):
        # Setup data for tests
        return {
            "freq_domain": np.linspace(1e9 - 5e6, 1e9 + 5e6, 100),
            "range_domain": np.linspace(0, 3000, 100),
            "aspect_domain": np.linspace(-45, 45, 64),
            "center_freq": 1e9,
        }

    def test_initialization_with_frequency_domain(self, setup_data):
        dt = DomainTransforms(freq_domain=setup_data["freq_domain"])
        assert dt.num_freq == len(setup_data["freq_domain"])
        assert dt.delta_freq == pytest.approx(setup_data["freq_domain"][1] - setup_data["freq_domain"][0])
        assert dt.center_freq == setup_data["freq_domain"][len(setup_data["freq_domain"]) // 2]
        assert dt.fft_bandwidth == pytest.approx(len(setup_data["freq_domain"]) * dt.delta_freq)

    def test_initialization_with_range_domain(self, setup_data):
        dt = DomainTransforms(range_domain=setup_data["range_domain"], center_freq=setup_data["center_freq"])
        assert dt.range_resolution == pytest.approx(setup_data["range_domain"][1] - setup_data["range_domain"][0])
        assert dt.range_period == pytest.approx(setup_data["range_domain"][-1] + dt.range_resolution)
        assert dt.freq_domain is not None
        assert dt.center_freq == setup_data["center_freq"]

    def test_initialization_with_aspect_domain(self, setup_data):
        dt = DomainTransforms(aspect_domain=setup_data["aspect_domain"], center_freq=setup_data["center_freq"])
        assert dt.aspect_angle == pytest.approx(setup_data["aspect_domain"][-1] - setup_data["aspect_domain"][0])
        assert dt.num_aspect_angle == len(setup_data["aspect_domain"])
        assert dt.range_domain is None
        assert dt.range_period is not None
        assert dt.range_resolution is not None

    def test_invalid_initialization(self, setup_data):
        # Passing multiple domains should raise a RuntimeError
        with pytest.raises(RuntimeError, match="Incorrect number of domains were passed to 'DomainTransforms'."):
            DomainTransforms(freq_domain=setup_data["freq_domain"], range_domain=setup_data["range_domain"])

    def test_missing_center_freq_with_range_domain(self, setup_data):
        # Missing center frequency with range domain should raise a RuntimeError
        with pytest.raises(RuntimeError, match="Center frequency is missing."):
            DomainTransforms(range_domain=setup_data["range_domain"])

    def test_missing_center_freq_with_aspect_domain(self, setup_data):
        # Missing center frequency with aspect domain should raise a RuntimeError
        with pytest.raises(RuntimeError, match="Center frequency is missing."):
            DomainTransforms(aspect_domain=setup_data["aspect_domain"])

    def test_calculated_range_domain(self, setup_data):
        dt = DomainTransforms(freq_domain=setup_data["freq_domain"])
        expected_range_resolution = SpeedOfLight / dt.fft_bandwidth / 2
        expected_range_period = dt.num_freq * expected_range_resolution

        assert dt.range_resolution == pytest.approx(expected_range_resolution)
        assert dt.range_period == pytest.approx(expected_range_period)
        assert len(dt.range_domain) == dt.num_freq

    def test_calculated_aspect_domain(self, setup_data):
        dt = DomainTransforms(range_domain=setup_data["range_domain"], center_freq=setup_data["center_freq"])
        dt.calculate_aspect_domain()

        assert dt.num_aspect_angle > 0
        assert dt.aspect_angle > 0

    def test_fft_bandwidth_to_freq_domain(self, setup_data):
        dt = DomainTransforms(range_domain=setup_data["range_domain"], center_freq=setup_data["center_freq"])
        with pytest.raises(RuntimeError):
            dt.fft_bandwidth_to_freq_domain(None, None, None)

    def test_split_num_units(self):
        assert split_num_units("1^2mm")
        assert split_num_units("1mm")
        assert split_num_units("@mm")

    def test_unit_converter_rcs(self):
        assert unit_converter_rcs("1m", "meter") == Quantity("1m")
        assert unit_converter_rcs("1", "deg", default_unit_system="Angle") == Quantity("1deg")
