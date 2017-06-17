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
import structure_threader.wrappers.maverick_wrapper as mw


class Arguments():
    """
    Bogus class to work a mock for the "args" attributes from argparse.
    """
    def __init__(self):
        self.external_prog = "EP"
        self.infile = "IF"
        self.outpath = ""
        self.params = "PA"
        self.notests = False
        self.Ks = [2, 3, 4, 5]


def test_mav_cli_generator():
    """
    Tests if mav_cli_generator() is working correctlly.
    """
    # Define arguments
    arg = Arguments()
    k_val = 4

    mock_cli = ["EP", "-Kmin", str(k_val), "-Kmax", str(k_val), "-data",
                "IF", "-outputRoot", "mav_K4/", "-masterRoot", "/",
                "-parameters", "PA"]

    # Perform test with and without TI
    for ti_value in (False, True):
        arg.notests = ti_value
        if arg.notests is True:
            mock_cli += ["-thermodynamic_on", "f"]

        returned_cli, out_dir = mw.mav_cli_generator(arg, k_val)
        assert returned_cli == mock_cli
        assert out_dir == "mav_K4/"


def test_mav_params_parser():
    """
    Tests if mav_params_parser() is working correctlly.
    """
    assert mw.mav_params_parser("smalldata/parameters.txt") is True
    assert mw.mav_params_parser("smalldata/parameters_f.txt") is False
