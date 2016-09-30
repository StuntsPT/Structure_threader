#!/usr/bin/python3

# Copyright 2015-2016 Francisco Pina Martins <f.pinamartins@gmail.com>
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
            print("WARNING: Number of specified threads is higher than the "
                  "available ones. Adjusting number of threads to {}, "
                  "which is the total number of CPUs (physical and logical) on "
                  "this machine.".format(os.cpu_count()))
            threads = os.cpu_count()
        else:
            threads = asked_threads
    except:
        threads = asked_threads
    return threads


def file_checker(path, msg=None, is_file=True):
    """
    Verify the existance of a given path. Raise an error if not present.
    :param path: string, path to file/directory
    :param msg: string, optional custom error message
    :param if_file, True if path is a file, False if a dir
    """
    if is_file is False:
        if not os.path.exists(path) or not os.path.isdir(path):
            try:
                os.makedirs(path)
            except FileExistsError:
                if not msg:
                    print("ERROR: '{}' should be the path to a directory, not "
                          "to a file.'".format(path))
                else:
                    print("ERROR: {}".format(msg))
                raise SystemExit(1)
    else:
        if os.path.isdir(path):
            if not msg:
                print("ERROR: '{}' should be the path to a file, not to a "
                      "directory.'".format(path))
            else:
                print("ERROR: {}".format(msg))
            raise SystemExit(1)
        elif not os.path.exists(path):
            if not msg:
                print("ERROR: Path '{}' does not exist".format(path))
            else:
                print("ERROR: {}".format(msg))
            raise SystemExit(1)
