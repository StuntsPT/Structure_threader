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
import mockups
import structure_threader.wrappers.maverick_wrapper as mw


def test_mav_cli_generator():
    """
    Tests if mav_cli_generator() is working correctlly.
    """
    # Define arguments
    arg = mockups.Arguments()
    k_val = 4
    parameters = {}

    mock_cli = ["EP", "-Kmin", str(k_val), "-Kmax", str(k_val), "-data",
                "IF", "-outputRoot", "mav_K4/", "-masterRoot", "/",
                "-parameters", "smalldata/parameters.txt"]

    # Perform test with and without TI
    for ti_value in (False, True):
        arg.notests = ti_value
        if arg.notests is True:
            mock_cli += ["-thermodynamic_on", "f"]

        returned_cli, out_dir = mw.mav_cli_generator(arg, k_val, parameters)
        assert returned_cli == mock_cli
        assert out_dir == "mav_K4/"


def test_mav_ti_in_use():
    """
    Tests if mav_params_parser() is working correctlly.
    """
    assert mw.mav_ti_in_use({"thermodynamic_on": "1"}) is True
    assert mw.mav_ti_in_use({"thermodynamic_on": "0"}) is False
    assert mw.mav_ti_in_use({}) is True


def test_mav_alpha_failsafe():
    """
    Tests if mav_alpha_failsafe() is working correctlly.
    """
    k_list = [2, 3, 4, 5]
    mock_params = [{"alpha": "1", "alphaPropSD": "0.1"},
                   {"alpha": "0.9,0.8,0.7,0.6", "alphaPropSD": "0.1"},
                   {"alpha": "1", "alphaPropSD": "0.09,0.08,0.07,0.06"},
                   {"alpha": "0.9,0.8,0.7,0.6",
                    "alphaPropSD": "0.09,0.08,0.07,0.06"}]

    expected_results = [{"alpha": False, "alphaPropSD": False},
                        {"alpha": {2: "0.9", 3: "0.8", 4: "0.7", 5: "0.6"},
                         "alphaPropSD": False},
                        {"alpha": False,
                         "alphaPropSD": {2: "0.09", 3: "0.08", 4: "0.07",
                                         5: "0.06"}},
                        {"alpha": {2: "0.9", 3: "0.8", 4: "0.7", 5: "0.6"},
                         "alphaPropSD": {2: "0.09", 3: "0.08", 4: "0.07",
                                         5: "0.06"}}]
    for exp, mck in zip(expected_results, mock_params):
        assert mw.mav_alpha_failsafe(mck, k_list) == exp


def test_maverick_merger():
    """
    Tests if maverick_merger() is working correctlly.
    """

    def _hash_function(dir_to_test):
        """
        A function to generate sha256 checksum of all contents of a directory.
        """
        fnamelst = os.listdir(dir_to_test)
        # Skip the file that contains randomized data
        fnamelst = [x for x in fnamelst if x != "outputEvidenceNormalised.csv"]
        fnamelst = [os.path.join(dir_to_test, fname) for fname in fnamelst]
        hashes = [(hashlib.sha256(open(fname, 'rb').read()).digest())
                  for fname in fnamelst]

        return hashes

    mav_params = mw.mav_params_parser("smalldata/parameters.txt")
    mw.maverick_merger("files", [1, 2, 3], mav_params, False)
    known_hashes = _hash_function("files/test_merged")
    generated_hashes = _hash_function("files/merged")

    assert known_hashes == generated_hashes
