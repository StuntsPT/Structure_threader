#!/usr/bin/python3

# Copyright 2015-2021 Francisco Pina Martins <f.pinamartins@gmail.com>
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

import argparse
import sys
import os

try:
    import sanity_checks.sanity as sanity
except ImportError:
    import structure_threader.sanity_checks.sanity as sanity


def argument_parser(args):
    """
    Parses the list of arguments as implemented in argparse.
    """
    parser = argparse.ArgumentParser(
        description="A software wrapper to paralelize genetic clustering "
                    "programs.",
        prog="Structure_threader",
        formatter_class=argparse.RawTextHelpFormatter)

    # Create subparsers for each main structure_threader  operation
    subparsers = parser.add_subparsers(
        help="Select which structure_threader command you wish to "
             "execute.",
        dest="main_op")

    run_parser = subparsers.add_parser("run", help="Performs a complete"
                                       " run of structure_threader.")
    plot_parser = subparsers.add_parser("plot", help="Performs only the"
                                        " plotting operations.")
    param_parser = subparsers.add_parser("params", help="Generates mainparams "
                                         "and extraparams files.")

    # ####################### RUN ARGUMENTS ###################################
    # Group definition
    io_opts = run_parser.add_argument_group("Input/Output options")
    id_opts = run_parser.add_argument_group(
        "Individual/Population identification options")
    main_exec = run_parser.add_argument_group(
        "Program execution options. Mutually exclusive")
    k_opts = run_parser.add_argument_group("Cluster options")
    run_opts = run_parser.add_argument_group("Structure run options")
    plot_opts = run_parser.add_argument_group("Q-matrix plotting options")
    misc_opts = run_parser.add_argument_group("Miscellaneous options")

    # Group options
    main_exec_ex = main_exec.add_mutually_exclusive_group(required=True)
    k_opts = k_opts.add_mutually_exclusive_group(required=True)
    id_opts = id_opts.add_mutually_exclusive_group(required=False)

    main_exec_ex.add_argument("-st", dest="external_prog", type=str,
                              default=None,
                              metavar="filepath",
                              help="Location of the structure executable "
                              "in  your environment.")
    main_exec_ex.add_argument("-fs", dest="external_prog", type=str,
                              default=None,
                              metavar="filepath",
                              help="Location of the fastStructure "
                              "executable in your environment.")
    main_exec_ex.add_argument("-mv", dest="external_prog", type=str,
                              default=None,
                              metavar="filepath",
                              help="Location of the MavericK executable "
                              "in your environment.")
    main_exec_ex.add_argument("-als", dest="external_prog", type=str,
                              default=None,
                              metavar="filepath",
                              help="Location of the ALStructure script "
                              "in your environment.")

    k_opts.add_argument("-K", dest="k_list", type=int,
                        help="Number of Ks to calculate.\n",
                        metavar="int")
    k_opts.add_argument("-Klist", dest="k_list", nargs="+",
                        type=int,
                        help="List of Ks to calculate.\n",
                        metavar="'2 4 6'")

    run_opts.add_argument("-R", dest="replicates", type=int, required=False,
                          help="Number of replicate runs for each value "
                          "of K (default:%(default)s).\nIgnored for "
                          "fastStructure, MavericK and ALStructure",
                          metavar="int", default=20)

    io_opts.add_argument("-i", dest="infile", type=str, required=True,
                         help="Input file.\n", metavar="infile")
    io_opts.add_argument("-o", dest="outpath", type=str, required=True,
                         help="Directory where the results will be "
                         "stored in.\n",
                         metavar="output_directory")
    io_opts.add_argument("--params", dest="params", type=str, required=False,
                         help="File with run parameters.",
                         metavar="parameters_file.txt", default=None)

    id_opts.add_argument("--pop", dest="popfile", type=str, required=False,
                         help="File with population information.",
                         metavar="popfile", default=None)
    id_opts.add_argument("--ind", dest="indfile", type=str, required=False,
                         help="File with population information.",
                         metavar="indfile", default=None)

    misc_opts.add_argument("-t", dest="threads", type=int, required=True,
                           help="Number of threads to use "
                                "(default:%(default)s).\n",
                           metavar="int", default=4)
    misc_opts.add_argument("--log", dest="log", type=bool, required=False,
                           help="Choose this option if you want to "
                           "enable logging.",
                           metavar="bool", default=False)
    misc_opts.add_argument("--no_tests", dest="notests", type=bool,
                           required=False,
                           help="Disable best K tests. Implies "
                           "--no_plots",
                           metavar="bool", default=False)
    misc_opts.add_argument("--extra_opts", dest="extra_options", type=str,
                           required=False,
                           help="Add extra arguments to pass to the "
                           "wrapped program here (between quotes).\nExamples: "
                           "\"prior=logistic\" for fastStructure\n"
                           "\"-D 12345\" for STRUCTURE",
                           metavar="string", default="")
    misc_opts.add_argument("--seed", dest="seed", type=int, required=False,
                           help="Define the random seed value to pass to "
                           "STRUCTURE and fastStructure",
                           default=1235813, metavar="int")

    plot_opts.add_argument("--no_plots", dest="noplot", type=bool,
                           required=False, help="Disable plot drawing.",
                           metavar="bool", default=False)
    plot_opts.add_argument("--override_bestk", dest="bestk", type=int,
                           required=False, nargs="+",
                           help="Override 'K' values from the given list"
                           " to be ploteted in the combined figure.",
                           metavar="'2 4 5'", default=None)
    plot_opts.add_argument("-bw", dest="blacknwhite",
                           action="store_const", const=True,
                           help="Set this flag to draw greyscale plots"
                           " instead of colored ones.")
    plot_opts.add_argument("--use-ind-labels", dest="use_ind",
                           action="store_const", const=True,
                           help="Use the individual labels in the "
                                "structure plot instead of population"
                                " labels")

    # ####################### PLOT ARGUMENTS ##################################
    # Group definitions

    main_opts = plot_parser.add_argument_group("Main plotting options")
    extra_opts = plot_parser.add_argument_group("Extra plotting options")
    sort_opts = plot_parser.add_argument_group("Plot sorting options")

    # Group options
    sort_opts_ex = sort_opts.add_mutually_exclusive_group(required=True)

    main_opts.add_argument("-i", dest="results_path", type=str, required=True,
                           help="The directory where output meanQ files you "
                                "want to plot are located. "
                                "If plotting MavericK results, provide "
                                "the directory where the directories named "
                                "`mav_KX` are located.")
    main_opts.add_argument("-f", dest="program", type=str, required=True,
                           choices=["structure", "faststructure",
                                    "maverick"],
                           help="The format of the result files.")
    main_opts.add_argument("-K", dest="bestk", nargs="+", required=True,
                           help="Choose the K values to plot. Each K "
                                "value provided will be plotted "
                                "individually and a comparative plot "
                                "will all K's will be generated. "
                                "Example: -K 2 3 4.")
    main_opts.add_argument("-o", dest="outpath", type=str, default=".",
                           help="The directory where the plots will be "
                                "generated. If it is not provided, "
                                "the current working directory "
                                "will be used.")

    extra_opts.add_argument("-bw", dest="blacknwhite",
                            action="store_const", const=True,
                            help="Set this flag to draw greyscale plots "
                                 "instead of colored ones.")
    extra_opts.add_argument("--use-ind-labels", dest="use_ind",
                            action="store_const", const=True,
                            help="Use the individual labels in the "
                                 "structure plot instead of population "
                                 "labels")

    sort_opts_ex.add_argument("--pop", dest="popfile", type=str,
                              required=False,
                              help="File with population information.",
                              metavar="popfile", default=None)
    sort_opts_ex.add_argument("--ind", dest="indfile", type=str,
                              required=False,
                              help="File with individual information.",
                              metavar="indfile", default=None)

    # ####################### PARAM ARGUMENTS ##############################
    # Group definition
    io_opts = param_parser.add_argument_group("Input/Output options")

    # Group options
    io_opts.add_argument("-o", dest="outpath", type=str, required=True,
                         help="Directory where the parameter files will be "
                         "written.\n",
                         metavar="output_directory")

    # ################### END OF SPECIFIC CODE ###############################
    arguments = parser.parse_args(args)

    # Perform sanity checks on arguments
    arguments = argument_sanity(arguments, parser)

    # Perform modifications on arguments
    arguments = argument_modifications(arguments)

    return arguments


def argument_sanity(arguments, parser):
    """
    Performs some sanity checks on the user provided arguments.
    """
    if arguments.main_op == "run":
        # External program
        sanity.file_checker(arguments.external_prog,
                            "Could not find your external program in "
                            "the specified path "
                            "'{}'.".format(arguments.external_prog))

        # Input file
        sanity.file_checker(arguments.infile,
                            "The specified infile '{}' does not "
                            "exist.".format(arguments.infile))

        # Output dir
        sanity.file_checker(arguments.outpath,
                            "Output argument '{}' is pointing to an "
                            "existing file. This argument requires a "
                            "directory.".format(arguments.outpath), False)

        # Handle argparse limitations with "--" options.
        if arguments.extra_options != "":
            if "-st" not in sys.argv:
                arguments.extra_options = \
                    "--{0}".format(arguments.extra_options)
                arguments.extra_options = \
                    " --".join(arguments.extra_options.split())

        # fastStructure is really only usefull with either a pop or indfile...
        if "-fs" in sys.argv and\
            arguments.popfile is None and\
                arguments.indfile is None:
            parser.error("-fs requires either --pop or --ind.")

        # Make sure we provide paths for mainparams, extraparams and
        # parameters.txt  depending on the wrapped program.
        if arguments.params is not None:
            arguments.params = os.path.abspath(arguments.params)
        if "-mv" in sys.argv and arguments.params is None:
            parser.error("-mv requires --params.")
        elif "-mv" in sys.argv:
            sanity.file_checker(os.path.abspath(arguments.params))
        elif "-st" in sys.argv and arguments.params is None:
            arguments.params = os.path.join(os.path.dirname(arguments.infile),
                                            "mainparams")

        # Number of replicates
        arguments.replicates = range(1, arguments.replicates + 1)

        arguments.threads = sanity.cpu_checker(arguments.threads)

    elif arguments.main_op == "plot":
        if arguments.program == "faststructure" and arguments.popfile is None\
                and arguments.indfile is None:
            parser.error("fastStructure plots require either --pop or --ind.")

    elif arguments.main_op == "run" or arguments.main_op == "plot":
        # Check the existance of several files:
        # Popfile
        if arguments.popfile is not None:
            sanity.file_checker(arguments.popfile,
                                "The specified popfile '{}' does not "
                                "exist.".format(arguments.popfile))
        # Indfile
        if arguments.indfile is not None:
            sanity.file_checker(arguments.indfile,
                                "The specified indfile '{}' does not "
                                "exist.".format(arguments.indfile))

    return arguments


def argument_modifications(arguments):
    """
    Performs some eventually necessary changes to the arguments and returns
    them.
    """
    # Transform a single K value into a list
    if arguments.main_op == "run":
        if isinstance(arguments.k_list, int):
            arguments.k_list = range(1, arguments.k_list + 1)

        # Switch relative to absolute paths
        arguments.infile = os.path.abspath(arguments.infile)
        arguments.outpath = os.path.abspath(arguments.outpath)

    return arguments
