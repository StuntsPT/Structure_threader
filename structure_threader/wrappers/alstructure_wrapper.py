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

import os
import logging


try:
    import colorer.colorer as colorer
except ImportError:
    import structure_threader.colorer.colorer as colorer


def alstr_cli_generator(arg, k_val):
    """
    Generates and returns command line for running ALStructure.
    """
    output_file = os.path.join(arg.outpath, "alstr_K" + str(k_val))
    if arg.infile.endswith((".bed", ".fam", ".bim")):
        infile = arg.infile[:-4]
    elif arg.infile.endswith(".vcf"):
        vcf_to_matrix(arg.infile)
        infile = arg.infile[:-4] + ".tsv"

    cli = ["Rscript", arg.external_prog, infile, str(k_val), output_file]

    return cli, output_file


def vcf_to_matrix(vcf_file):
    """
    Parses a VCF file and converts it to a tsv matrix that can be read by
    ALStructure.
    Takes a VCF filename as input.
    Does not return anything.
    Writes a new file with the same name as the VCF but with .tsv extension
    """
    conversion_table = {"0/0": "0", "0/1": "1", "1/0": "1", "1/1": "2",
                        "0|0": "0", "0|1": "1", "1|0": "1", "1|1": "2"}

    outfile = open(vcf_file.replace(".vcf", ".tsv"), "w")
    infile = open(vcf_file, "r")

    # Skip initial comments that starts with #
    while True:
        line = infile.readline()
        # break while statement if it is not a comment line
        # i.e. does not startwith #
        if not line.startswith('#'):
            break

    while line:
        genotypes = line.split()[9:]
        converted = [conversion_table[x.split(":")[0]]
                     if x.split(":")[0] in conversion_table
                     else "NA" for x in genotypes]
        outfile.write("\t".join(converted) + "\n")
        try:
            line = infile.readline()
        except IOError:
            break
    infile.close()
    outfile.close()
