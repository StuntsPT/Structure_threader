#!/usr/bin/python3

# Copyright 2016 Francisco Pina Martins <f.pinamartins@gmail.com>
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
import structure_threader.sanity_checks.sanity as sc


def test_cpu_checker():
    """
    Tests if cpu_checker() is working correctlly.
    """
    assert sc.cpu_checker(1) == 1
    assert sc.cpu_checker(os.cpu_count() + 1) == os.cpu_count()


def test_file_checker(tmpdir):
    """
    Tests if file_checker() is working correctlly.
    """
    testdir = tmpdir.mkdir("sub")
    testfile = testdir.join("filetest.txt")
    testfile.write("content")

    # Correctly check for a file
    assert sc.file_checker(str(testfile)) is None
    # Correctlly check for a directory
    assert sc.file_checker(str(testdir), is_file=False) is None
    # Check for a file, but given a dir
    with pytest.raises(SystemExit):
        sc.file_checker(str(testdir))
    # Check for a dir, but given a file
    with pytest.raises(SystemExit):
        sc.file_checker(str(testfile), is_file=False)
    # Chck for a file and provided with a wrong path
    with pytest.raises(SystemExit):
        sc.file_checker(str(testfile) + "a")
