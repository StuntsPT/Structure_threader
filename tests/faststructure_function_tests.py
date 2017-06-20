#!/usr/bin/python3

# Copyright 2017 Francisco Pina Martins <f.pinamartins@gmail.com>
# This file is part of structure_threader.
# structure_threader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# structure_threader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with structure_threader. If not, see <http://www.gnu.org/licenses/>.


import os
import pytest
import mockups
import structure_threader.wrappers.faststructure_wrapper as fsw


def test_fs_cli_generator():
    """
    Tests if faststructure_cli_generator() is working correctlly.
    """
    # Define arguments
    arg = mockups.Arguments()
    k_val = 4

    # Test with a binary
    mock_cli = ["EP", "-K", str(k_val), "--input",
                "IF", "--output", "fS_run_K", "--format", "str",
                "--prior=logistic"]

    returned_cli = fsw.fs_cli_generator(k_val, arg)
    assert returned_cli == mock_cli

    # Test with a script
    arg.external_prog = "EP.py"
    mock_cli = ["python2", "EP.py", "-K", str(k_val), "--input",
                "IF", "--output", "fS_run_K", "--format", "str",
                "--prior=logistic"]

    returned_cli = fsw.fs_cli_generator(k_val, arg)
    assert returned_cli == mock_cli

    # TODO: deduplicate code.
