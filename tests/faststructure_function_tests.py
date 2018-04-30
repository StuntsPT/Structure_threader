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


import pytest
import mockups
import structure_threader.wrappers.faststructure_wrapper as fsw


def test_fs_cli_generator():
    """
    Tests if fs_cli_generator() is working correctlly.
    """
    # Define arguments
    arg = mockups.Arguments()
    k_val = 4

    for prog in ["EP", "EP.py"]:

        arg.external_prog = prog
        arg.seed = "1235813"
        mock_cli = [prog, "-K", str(k_val), "--input",
                    "IF", "--output", "fS_run_K", "--format", "str",
                    "--seed", "1235813", "--prior=logistic"]
        if prog.endswith(".py"):
            mock_cli = ["python2"] + mock_cli

        returned_cli, returned_outdir = fsw.fs_cli_generator(k_val, arg)

        assert returned_cli == mock_cli
        assert returned_outdir == "fS_run_K"
