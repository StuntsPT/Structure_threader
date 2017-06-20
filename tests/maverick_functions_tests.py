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

import hashlib
import os
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
        self.params = "smalldata/parameters.txt"
        self.notests = False
        self.k_list = [2, 3, 4, 5]


def test_mav_cli_generator():
    """
    Tests if mav_cli_generator() is working correctlly.
    """
    # Define arguments
    arg = Arguments()
    k_val = 4

    mock_cli = ["EP", "-Kmin", str(k_val), "-Kmax", str(k_val), "-data",
                "IF", "-outputRoot", "mav_K4/", "-masterRoot", "/",
                "-parameters", "smalldata/parameters.txt"]

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


def test_mav_alpha_failsafe():
    """
    Tests if mav_alpha_failsafe() is working correctlly.
    """
    k_list = [2, 3, 4, 5]
    assert mw.mav_alpha_failsafe("smalldata/parameters.txt", k_list) == {
        "alpha": False, "alphaPropSD": False}
    assert mw.mav_alpha_failsafe("smalldata/parameters_a.txt", k_list) == {
        "alpha": {2: "0.9", 3: "0.8", 4: "0.7", 5: "0.6"}, "alphaPropSD": False}
    assert mw.mav_alpha_failsafe("smalldata/parameters_as.txt", k_list) == {
        "alpha": False,
        "alphaPropSD": {2: "0.09", 3: "0.08", 4: "0.07", 5: "0.06"}}
    assert mw.mav_alpha_failsafe("smalldata/parameters_a_as.txt", k_list) == {
        "alpha": {2: "0.9", 3: "0.8", 4: "0.7", 5: "0.6"},
        "alphaPropSD": {2: "0.09", 3: "0.08", 4: "0.07", 5: "0.06"}}


def test_maverick_merger():
    """
    Tests if maverick_merger() is working correctlly.
    """

    def _hash_function(dir_to_test):
        """
        A function to generate sha256 checksum of all contents of a directory.
        """
        fnamelst = os.listdir(dir_to_test)
        fnamelst = [os.path.join(dir_to_test, fname) for fname in fnamelst]
        hashes = [(hashlib.sha256(open(fname, 'rb').read()).digest())
                  for fname in fnamelst]

        return hashes

    mw.maverick_merger("files", [1, 2, 3], "smalldata/parameters.txt", False)
    known_hashes = _hash_function("files/test_merged")
    generated_hashes = _hash_function("files/merged")

    assert known_hashes == generated_hashes
