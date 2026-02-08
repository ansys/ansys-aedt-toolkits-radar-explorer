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

from ansys.aedt.core.generic.constants import SpeedOfLight


class DomainTransforms:
    def __init__(self, freq_domain=None, range_domain=None, aspect_domain=None, center_freq=None):
        self.__freq_domain = None
        # FFT bandwidth, including the extra df/2 tails on either side of the domain
        self.__fft_bandwidth = None
        self.__num_freq = None
        self.__delta_freq = None
        self.__center_freq = center_freq

        self.__range_resolution = None
        self.__range_period = None
        self.__range_upsample = 1

        self.__num_aspect_angle = None
        # Angular span, not including the tails,
        self.__aspect_angle = None

        self.__aspect_domain = aspect_domain
        self.__range_domain = range_domain

        num_not_none = 0
        if freq_domain is not None:
            num_not_none += 1
        if range_domain is not None:
            num_not_none += 1
        if aspect_domain is not None:
            num_not_none += 1

        if num_not_none != 1:  # pragma: no cover
            raise RuntimeError("Incorrect number of domains were passed to 'DomainTransforms'.")
        elif freq_domain is not None:
            self.__freq_domain = freq_domain
            self.compute_freq_domain_derived()
            self.calculate_range_domain()
        elif range_domain is not None:
            if center_freq is None:
                raise RuntimeError("Center frequency is missing.")
            self.compute_range_domain_derived()
            self.calculate_freq_domain()
            # always calculates even if it doesn't apply
            self.calculate_aspect_domain()
        elif aspect_domain is not None:
            if center_freq is None:
                raise RuntimeError("Center frequency is missing.")
            self.compute_aspect_domain_derived()
            self.calculate_range_domain_from_aspect()

    # TODO: __init__ should be refactored to compute freq_domain from bandwidth, then this method can be removed
    @staticmethod
    def fft_bandwidth_to_freq_domain(fft_bandwidth_hz, center_freq_hz, num_freq):
        """Convert FFT bandwidth to frequency domain."""
        if fft_bandwidth_hz is not None and center_freq_hz is not None and num_freq is not None:
            delta_freq = fft_bandwidth_hz / num_freq
            num_freq_step = num_freq - 1
            upper_half_steps = num_freq_step // 2
            lower_half_steps = num_freq_step - upper_half_steps
            return center_freq_hz + np.linspace(
                -lower_half_steps * delta_freq, upper_half_steps * delta_freq, num=num_freq
            )
        else:
            raise RuntimeError("'bandwidth', 'center_freq', and 'num_freq' must be defined.")

    @property
    def freq_domain(self):
        """Frequency domain."""
        return self.__freq_domain

    @property
    def fft_bandwidth(self):
        """FFT bandwidth."""
        return self.__fft_bandwidth

    @property
    def num_freq(self):
        return self.__num_freq

    @property
    def delta_freq(self):
        return self.__delta_freq

    @property
    def center_freq(self):
        return self.__center_freq

    @property
    def range_resolution(self):
        return self.__range_resolution

    @property
    def range_upsample(self):
        return self.__range_upsample

    @property
    def range_period(self):
        return self.__range_period

    @property
    def aspect_angle(self):
        return self.__aspect_angle

    @property
    def num_aspect_angle(self):
        return self.__num_aspect_angle

    @property
    def range_domain(self):
        return self.__range_domain

    @property
    def aspect_domain(self):
        return self.__aspect_domain

    def compute_freq_domain_derived(self):
        if self.freq_domain is None:  # pragma: no cover
            raise RuntimeError("freq_domain is None")
        self.__num_freq = len(self.freq_domain)
        self.__delta_freq = self.freq_domain[1] - self.freq_domain[0]
        # Consistent with ADP definition, extra df/2 tails
        # adopt ADP conventions that the center frequency is the center sample for odd-length frequency domains,
        # or the first sample in the right half
        self.__fft_bandwidth = self.num_freq * self.delta_freq
        self.__center_freq = self.freq_domain[len(self.freq_domain) // 2]

    def compute_range_domain_derived(self):
        if self.range_domain is None:  # pragma: no cover
            raise RuntimeError("range_domain is None")
        self.__range_resolution = self.range_domain[1] - self.range_domain[0]
        self.__range_period = self.range_domain[-1] + self.range_resolution

    def compute_aspect_domain_derived(self):
        if self.aspect_domain is None:  # pragma: no cover
            raise RuntimeError("_aspect_domain is None")
        # this might not necessarily be correct
        # need an additional df
        self.__aspect_angle = self.aspect_domain[-1] - self.aspect_domain[0]
        self.__num_aspect_angle = len(self.aspect_domain)

    def calculate_range_domain(self):
        self.__range_resolution = SpeedOfLight / self.fft_bandwidth / 2  # the bandwidth is consistent with ADP
        self.__range_period = self.num_freq * self.range_resolution
        num_range = self.range_upsample * self.num_freq
        self.__range_domain = np.linspace(0, self.range_period - self.range_resolution, num=num_range)

    def calculate_freq_domain(self):
        self.__fft_bandwidth = SpeedOfLight / (2 * self.range_resolution)
        self.__num_freq = len(self.range_domain)
        self.__delta_freq = self.fft_bandwidth / self.num_freq
        freqstart = self.center_freq - np.floor(0.5 * self.num_freq) * self.delta_freq
        freqstop = self.center_freq + (self.num_freq - 1) * self.delta_freq
        self.__freq_domain = np.linspace(freqstart, freqstop, num=self.num_freq)

    def calculate_aspect_domain(self):
        self.__num_aspect_angle = int(np.ceil(self.range_period / self.range_resolution))
        if self.center_freq:
            d_ang = SpeedOfLight / self.center_freq / 2 / self.range_period * 180 / np.pi
            self.__aspect_angle = d_ang * (self.num_aspect_angle - 1)

    def calculate_range_domain_from_aspect(self):
        d_ang = self.aspect_angle / (self.num_aspect_angle - 1)

        if self.center_freq:
            self.__range_period = SpeedOfLight / self.center_freq / 2 / d_ang * 180 / np.pi
            self.__range_resolution = self.range_period / self.num_aspect_angle
        else:  # pragma: no cover
            raise RuntimeError("Center frequency must be defined for domain from aspect.")
