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
        self.extra_options = "--prior=logistic"
        self.exec_mode = "EM"
        self.init = None
        self.nad_cpus = 0
        self.nad_gpus = 0
        self.supervised = False
        self.popfile = None
