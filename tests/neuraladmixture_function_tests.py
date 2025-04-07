#!/usr/bin/python3

# Copyright 2025 Francisco Pina Martins <f.pinamartins@gmail.com>
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

import pytest
import mockups
import structure_threader.wrappers.neuraladmixture_wrapper as nadw


def test_nad_cli_generator():
    """
    Tests if nad_cli_generator() is working correctlly.
    """
    # Define arguments
    arg = mockups.Arguments()
    k_val = 4
    seed = 42

    # arg.external_prog, arg.exec_mode, run_name, str(k_val), arg.infile, output_dir

    mock_cli = ["EP", "train", "--name", "nad_K4", "--k", str(k_val), "--data_path",
                "IF", "--save_dir", "nad_K4/", "--seed", str(seed)]

    returned_cli, run_name, out_dir = nadw.nad_cli_generator(arg, k_val, seed)
    assert returned_cli == mock_cli
    assert run_name == "nad_K4"
    assert out_dir == "nad_K4/"
