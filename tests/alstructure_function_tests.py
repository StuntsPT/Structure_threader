#!/usr/bin/python3

# Copyright 2019 Francisco Pina Martins <f.pinamartins@gmail.com>
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
import filecmp
import structure_threader.wrappers.alstructure_wrapper as alsw


def test_alstr_cli_generator():
    """
    Tests if alstr_cli_generator() is working correctlly.
    """
    # Define arguments
    arg = mockups.Arguments()
    arg.infile += ".bed"
    k_val = 4

    # "Rscript", arg.external_prog, infile, str(k_val), output_file

    mock_cli = ["Rscript", "EP", "IF", str(k_val), "alstr_K4"]

    returned_cli, out_file = alsw.alstr_cli_generator(arg, k_val)
    assert returned_cli == mock_cli
    assert out_file == "alstr_K4"


def test_vcf_to_matrix():
    """
    Tests if vcf_to_matrix() is working correctlly.
    Converts a known file, and compares the result with a known good conversion
    """
    # Define arguments
    arg = mockups.Arguments()
    arg.infile = "data/SmallTestData.vcf"
    k_val = 4
    alsw.vcf_to_matrix(arg.infile)

    assert filecmp.cmp(arg.infile[:-4] + ".tsv",
                       "data/SmallTestData_reference.tsv")
