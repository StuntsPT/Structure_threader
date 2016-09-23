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
import structure_threader.sanity_checks as sc

def cpu_checker_tester():
    """
    Tests if CPU checker routine works correctly.
    """
    cpus = os.cpu_count()

    for cases in range(1, cpus):
        assert sc.cpu_checker(cases, cpus) == cases

    assert sc.cpu_checker(cpus + 1, cpus) == cpus
