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

import string

from ansys.aedt.core.generic.constants import SI_UNITS
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.constants import unit_system


def split_num_units(value: str):
    """Split a string into a number and its unit.

    Parameters
    ----------
    value : str
        Text containing a value and a unit.

    Returns
    -------
    float, str
        Value extracted from the string, and unit

    Examples
    --------
    >>> value, unit = split_num_units("2.0GHz")
    >>> value, unit = split_num_units("3m^2")

    """
    if "^" in value:
        value = value.replace("^", "")
    value = value.replace(" ", "")
    new_value = value.rstrip(string.ascii_letters)
    units = value[len(new_value) :]
    try:
        value_float = float(new_value)
    except ValueError:
        value_float = 1.0
    return value_float, units


def unit_converter_rcs(value: str, new_units: str, default_unit_system: str = "Length") -> float | list:
    """Given a string containing a value in a certain unit, convert the value to another unit.

    Parameters
    ----------
    value : str
        Text containing a value and a unit.
    new_units: str
        Output units.
    input_unidefault_unit_systemt_system : str, default: ``"Length"`
        Default unit system if value does not have units.

    Returns
    -------
    float, list
        Values converted to new unit.

    Examples
    --------
    >>> value = unit_converter_rcs("2.0GHz", "Hz")  # 2000000000
    """
    new_value, old_unit = split_num_units(value)
    if old_unit == "m":
        # "m" is not the unit for meter in AEDT, so we need to convert it to "meter"
        old_unit = "meter"

    new_unit_system = SI_UNITS[default_unit_system]
    # Default PyAEDT angle unit is "rad", it is better to convert to "deg"
    if default_unit_system == "Angle":
        new_unit_system = "deg"
    if old_unit:
        new_unit_system = unit_system(old_unit)

    return unit_converter(new_value, unit_system=new_unit_system, input_units=old_unit, output_units=new_units)
