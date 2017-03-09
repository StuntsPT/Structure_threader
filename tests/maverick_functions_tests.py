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
import structure_threader.structure_threader as st


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

    st.maverick_merger("files", [1, 2, 3], False)
    known_hashes = _hash_function("files/test_merged")
    generated_hashes = _hash_function("files/merged")

    assert known_hashes == generated_hashes
