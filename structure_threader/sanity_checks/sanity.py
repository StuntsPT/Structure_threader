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
import logging

try:
    import colorer.colorer as colorer
except ImportError:
    import structure_threader.colorer.colorer as colorer

from collections import Counter

import numpy as np

# Set default log level and format
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

class AuxSanity(object):

    def log_error(self, msg, aux):

        logging.critical("Badly formatted {f1}file (provided with --{f1})"
                         " with error:\n\n"
                         "{f2}\n\n"
                         "Please correct the provided {f1}file and re-run"
                         " the plotting operation of structure_threader "
                         "with the following command:\n\n"
                         "structure_threader plot <opts>".format(
                             f1=aux, f2=msg))
        raise SystemExit

    def ind_mismatch(self, exp_array, kvals):

        mismatch = []

        for kobj in kvals.values():
            if exp_array.shape[0] != kobj.qvals.shape[0]:
                mismatch.append("{}: {} individuals (expected from "
                                "popfile: {})".format(kobj.file_path,
                                                      kobj.qvals.shape[0],
                                                      exp_array.shape[0]))

        return mismatch

    def check_popfile(self, filepath, kvals, **kwargs):
        """
        Check if the popfile" is valid.
        """
        # Try to load array from popfile
        try:
            poparray = np.genfromtxt(filepath,
                                     dtype=[("popname", "|U20"),
                                            ("nind", int),
                                            ("original_order", int)],
                                     loose=False)
        except ValueError as exc:
            self.log_error(exc, "pop")

        index = poparray["original_order"]

        # Check if order in third column has only unique fields
        dups = [str(x) for x, count in Counter(index).items() if count > 1]
        if dups:
            self.log_error("Order values in the third column of the "
                           "popfile must be unique. The following"
                           " indexes were repeated: {}".format(
                               " ".join(dups)), "pop")

        # Check if there is no gap in the range of the ordering
        missing = [str(x) for x in range(max(index)) if
                   x != 0 and x not in index]
        if missing:
            self.log_error("The order values in the third column of the"
                           " popfile must be in consecutive order."
                           " The following index(es) is(are) missing:"
                           " {}".format(" ".join(missing)), "pop")

        # Expand poprarray matrix with the frequency of each population
        exp_array = None
        for idx, val in enumerate(poparray):
            if exp_array is None:
                exp_array = np.repeat(poparray[idx:idx + 1, np.newaxis],
                                      val[1],
                                      0)
            else:
                exp_array = np.vstack(
                    [exp_array,
                     np.repeat(poparray[idx:idx + 1, np.newaxis],
                               val[1],
                               0)])

        # For each PlotK object, check if the poparray shape is compliant with
        # the qvals matrices
        mismatch = self.ind_mismatch(exp_array, kvals)

        if mismatch:
            self.log_error("The number of individuals specified in"
                           " the popfile does not match the number of"
                           " individuals in the meanQ files:\n{}".format(
                               "\n".join(mismatch)), "pop")

    def check_indfile(self, indfile, kvals):
        """
        Check if the "indfile" is valid.
        """
        try:
            indarray = np.genfromtxt(indfile, dtype="|U20")
        except ValueError as exc:
            self.log_error(exc, "ind")

        # The indfile may have between 1 to 3 columns. Depending on the number
        # of columns provided, the checks can vary.

        # Checks for single column
        if len(indarray.shape) != 1:
            single_array = indarray[:, 0]
        else:
            single_array = indarray
        # Check if number of individuals matches each qval matrix
        mismatch = self.ind_mismatch(single_array, kvals)
        if mismatch:
            self.log_error("The number of individuals specified in"
                           " the indfile does not match the number of"
                           " individuals in the meanQ files:\n{}".format(
                               "\n".join(mismatch)), "ind")

        if len(indarray.shape) != 1:
            if indarray.shape[1] == 3:
                # Check if third column is convertable into int
                try:
                    index = indarray[:, 2].astype(np.int64)
                except ValueError as exc:
                    self.log_error("The elements of the third column in"
                                   " the indfile must be integers:\n{}"
                                   "".format(exc), "ind")
                # Check if there is no gap in the range of the ordering
                missing = [str(x) for x in range(max(index)) if
                           x != 0 and x not in index]
                if missing:
                    self.log_error(
                        "The order values in the third column of the"
                        " indfile must be in consecutive order."
                        " The following index(es) is(are) missing:"
                        " {}".format(" ".join(missing)), "ind")


def cpu_checker(asked_threads):
    """Make cpu usage check to prevent excessive usage of threads.
    Returns the "ideal" number of threads to use."""
    try:
        if int(asked_threads) > os.cpu_count():
            logging.warning("Number of specified threads is higher than the "
                            "available ones. Adjusting number of threads to "
                            "{}, which is the total number of CPUs (physical "
                            "and logical) on this "
                            "machine.".format(os.cpu_count()))
            threads = os.cpu_count()
        else:
            threads = asked_threads
    except OSError:
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
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                os.makedirs(path)
            elif not os.access(path, os.W_OK | os.X_OK):
                raise PermissionError
        except FileExistsError:
            if not msg:
                logging.error("'{}' should be the path to a directory, not "
                              "to a file.'".format(path))
            else:
                logging.error("{}".format(msg))
            raise SystemExit(1)
        except PermissionError:
            logging.critical("Your user does not have permissions to write "
                             "to the results directory ({}). Either "
                             "chanage this path to one to which you have "
                             "write permissions to, or change the "
                             "permissions on this directory (if you "
                             "can).".format(path))
            raise SystemExit(1)

    else:
        if os.path.isdir(path):
            if not msg:
                logging.error("'{}' should be the path to a file, not to a "
                              "directory.'".format(path))
            else:
                logging.error("{}".format(msg))
            raise SystemExit(1)
        elif not os.path.exists(path):
            if not msg:
                logging.error("Path '{}' does not exist".format(path))
            else:
                logging.error("{}".format(msg))
            raise SystemExit(1)
