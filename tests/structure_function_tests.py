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
import structure_threader.wrappers.structure_wrapper as sw


def test_str_cli_generator():
    """
    Tests if str_cli_generator() is working correctlly.
    """
    # Define arguments
    arg = mockups.Arguments()
    k_val = 4
    outfile = "str_K4_rep1"
    arg.params = None
    seed = None

    mock_cli = ["EP", "-K", str(k_val), "-i", "IF", "-o", outfile]
    returned_cli, returned_outfile = sw.str_cli_generator(arg, k_val, 1, seed)

    assert returned_cli == mock_cli
    assert returned_outfile == outfile

    # Add a seed to the test
    seed = "1234"
    mock_cli += ["-D", "1234"]
    returned_cli, returned_outfile = sw.str_cli_generator(arg, k_val, 1, seed)

    assert returned_cli == mock_cli
    assert returned_outfile == outfile

    # Add an argument to the test
    arg.params = "test"

    mock_cli += arg.params
    returned_cli, returned_outfile = sw.str_cli_generator(arg, k_val, 1, seed)

    assert returned_cli == mock_cli
    assert returned_outfile == outfile


def test_str_param_checker():
    """
    Tests if the STRUCTURE parameter file checker is working.
    """
    arg = mockups.Arguments()
    arg.infile = "smalldata/Reduced_dataset.structure"
    arg.params = "mainparams"
    sw.str_param_checker(arg)
    assert arg.params == ["-m", "mainparams", "-e", "extraparams"]


def test_seed_generator():
    """
    Tests if the Seed generator is working as intended.
    """
    k_list = [1, 2]
    replicates = [1, 2, 3]
    extra_options = ""

    mock_jobs = [(2, 3), (2, 2), (2, 1), (1, 3), (1, 2), (1, 1)]
    returned_jobs = sw.seed_generator(extra_options, k_list, replicates)
    assert returned_jobs == mock_jobs

    # Add a seed option
    extra_options = "-D 1234"

    mock_jobs = [("7394266", 2, 3), ("1960426", 2, 2), ("125686", 2, 1),
                 ("1520747", 1, 3), ("9768157", 1, 2), ("585963", 1, 1)]
    returned_jobs = sw.seed_generator(extra_options, k_list, replicates)
    assert returned_jobs == mock_jobs
