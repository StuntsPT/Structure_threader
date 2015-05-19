#!/usr/bin/python3

# Copyright 2015 Francisco Pina Martins <f.pinamartins@gmail.com>
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


def cpu_checker(asked_threads):
    """Make cpu usage check to prevent excessive usage of threads.
    Returns the "ideal" number of threads to use."""
    try:
        if int(asked_threads) > os.cpu_count():
            print("WARNING: Number of specified threads is higher than the"
                  " available ones. Adjusting number of threads to %s" %
                  os.cpu_count())
            threads = os.cpu_count()
        else:
            threads = asked_threads
    except:
        threads = asked_threads
    return threads


def output_checker(outpath):
    """Verify the existence of requested output directory and create inexistent.
    Aborts execution if the outpath is a file."""
    if not os.path.exists(outpath) or not os.path.isdir(outpath):
        try:
            os.makedirs(outpath)
        except FileExistsError:
            print("ERROR: Output directory already exists.")
            raise SystemExit
