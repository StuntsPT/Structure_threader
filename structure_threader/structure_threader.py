#!/usr/bin/env python3
"""
structure_threader.py  —  drop-in CLI shim for the Snakemake-based workflow.

Accepts (almost) the same arguments as the original structure_threader,
translates them into a config.yaml, and invokes Snakemake.

Usage examples:

  # STRUCTURE — fully containerised
  structure_threader_smk run -st structure -K 6 -R 10 \\
      -i data/mydata.str -o results/ -t 8 --use-singularity

  # fastSTRUCTURE — fully containerised
  structure_threader_smk run -fs fastStructure -K 6 \\
      -i data/mydata.str -o results/ -t 8 --pop data/pops.txt --use-singularity

  # Re-plot from existing results
  structure_threader_smk plot -i results/ -f structure -K 3 -o results/plots/ \\
      --pop data/populations.txt

  # Generate STRUCTURE skeleton parameter files
  structure_threader_smk params -o data/

New arguments (Snakemake pass-through):
  --use-singularity   Run rules inside Singularity/Apptainer containers
  --use-docker        Run rules inside Docker containers
  --use-conda         Use per-rule conda environments
  --snakemake-args    Extra arguments forwarded verbatim to Snakemake
"""

import argparse
import os
import sys
import subprocess
import yaml
import logging

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_SNAKEFILE = os.path.join(_SCRIPT_DIR, "Snakefile")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="structure_threader_smk",
        description="structure_threader — Snakemake edition.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subs = parser.add_subparsers(dest="main_op",
                                 help="Select operation to perform.")

    # ── run ────────────────────────────────────────────────────────────────
    run = subs.add_parser("run", help="Perform a full run.")

    io = run.add_argument_group("Input / Output")
    io.add_argument("-i",       dest="infile",     required=True, metavar="FILE")
    io.add_argument("-o",       dest="outdir",     required=True, metavar="DIR")
    io.add_argument("--params", dest="mainparams", default=None,  metavar="FILE",
                    help="mainparams file [STRUCTURE only].")

    prog = run.add_argument_group("Wrapped program (mutually exclusive)")
    prog_ex = prog.add_mutually_exclusive_group(required=True)
    prog_ex.add_argument("-st",  dest="wrapper", action="store_const",
                         const="structure",
                         help="Wrap STRUCTURE.")
    prog_ex.add_argument("-fs",  dest="wrapper", action="store_const",
                         const="faststructure",
                         help="Wrap fastSTRUCTURE.")
    prog_ex.add_argument("-mv",  dest="wrapper", action="store_const",
                         const="maverick",
                         help="Wrap MavericK (not yet ported).")
    prog_ex.add_argument("-als", dest="wrapper", action="store_const",
                         const="alstructure",
                         help="Wrap ALStructure (not yet ported).")
    prog_ex.add_argument("-nad", dest="wrapper", action="store_const",
                         const="neuraladmixture",
                         help="Wrap NeuralAdmixture (not yet ported).")

    k = run.add_argument_group("K options (provide exactly one)")
    k_ex = k.add_mutually_exclusive_group(required=True)
    k_ex.add_argument("-K",     dest="K",      type=int,       metavar="INT")
    k_ex.add_argument("-Klist", dest="K_list", nargs="+", type=int, metavar="INT")

    ro = run.add_argument_group("Run options")
    ro.add_argument("-R",  dest="replicates", type=int, default=20, metavar="INT",
                    help="Replicates per K [STRUCTURE only, default: 20].")
    ro.add_argument("-t",  dest="threads",    type=int, default=4,  metavar="INT",
                    help="Parallel jobs / Snakemake --cores (default: 4).")
    ro.add_argument("--seed",      dest="seed",     type=int, default=1235813)
    ro.add_argument("--extra_opts",dest="extra_opts",default="", metavar="STR")
    ro.add_argument("--prior",     dest="fs_prior", default="simple",
                    choices=["simple", "logistic"],
                    help="fastSTRUCTURE prior (default: simple).")

    ids = run.add_argument_group("Individual / Population labels")
    ids_ex = ids.add_mutually_exclusive_group()
    ids_ex.add_argument("--pop", dest="popfile", default=None, metavar="FILE")
    ids_ex.add_argument("--ind", dest="indfile", default=None, metavar="FILE")

    pl = run.add_argument_group("Plot / analysis options")
    pl.add_argument("--no_tests",  dest="no_tests",    action="store_true")
    pl.add_argument("--no_plots",  dest="no_plots",    action="store_true")
    pl.add_argument("-bw",         dest="blacknwhite",  action="store_true")
    pl.add_argument("--use-ind-labels", dest="use_ind", action="store_true")

    sm = run.add_argument_group("Snakemake / container options")
    sm.add_argument("--use-singularity", dest="use_singularity", action="store_true")
    sm.add_argument("--use-docker",      dest="use_docker",      action="store_true")
    sm.add_argument("--use-conda",       dest="use_conda",       action="store_true")
    sm.add_argument("--snakefile",       dest="snakefile",
                    default=_DEFAULT_SNAKEFILE, metavar="FILE")
    sm.add_argument("--snakemake-args",  dest="snakemake_args",
                    default="", metavar="STR")
    sm.add_argument("--structure-image",     dest="structure_image",
                    default=None, metavar="URI")
    sm.add_argument("--faststructure-image", dest="faststructure_image",
                    default=None, metavar="URI")

    # ── plot ───────────────────────────────────────────────────────────────
    plot = subs.add_parser("plot", help="Re-draw plots from existing results.")

    pm = plot.add_argument_group("Main options")
    pm.add_argument("-i", dest="results_path", required=True, metavar="DIR")
    pm.add_argument("-f", dest="program",      required=True,
                   choices=["structure", "faststructure", "maverick", "alstructure"])
    pm.add_argument("-K", dest="bestk",        required=True, nargs="+", metavar="INT")
    pm.add_argument("-o", dest="outpath",      default=".", metavar="DIR")
    pe = plot.add_argument_group("Extra options")
    pe.add_argument("-bw",              dest="blacknwhite", action="store_true")
    pe.add_argument("--use-ind-labels", dest="use_ind",     action="store_true")
    ps = plot.add_argument_group("Sorting (provide one)")
    ps_ex = ps.add_mutually_exclusive_group(required=True)
    ps_ex.add_argument("--pop", dest="popfile", default=None, metavar="FILE")
    ps_ex.add_argument("--ind", dest="indfile", default=None, metavar="FILE")

    # ── params ─────────────────────────────────────────────────────────────
    params = subs.add_parser("params",
                             help="Generate skeleton STRUCTURE parameter files.")
    params.add_argument("-o", dest="outpath", required=True, metavar="DIR")

    return parser


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

_PORTED = {"structure", "faststructure"}

def handle_run(arg):
    if arg.wrapper not in _PORTED:
        logging.error(
            f"Wrapper '{arg.wrapper}' is not yet ported to the Snakemake edition.\n"
            f"Available: {', '.join(sorted(_PORTED))}.\n"
            "Use the original structure_threader for other wrappers."
        )
        sys.exit(1)

    # fastSTRUCTURE requires --pop or --ind
    if arg.wrapper == "faststructure" and not arg.popfile and not arg.indfile:
        logging.error("-fs requires either --pop or --ind.")
        sys.exit(1)

    # Sanity checks
    for label, path in [("infile",     arg.infile),
                         ("mainparams", arg.mainparams),
                         ("popfile",    arg.popfile),
                         ("indfile",    arg.indfile)]:
        if path and not os.path.isfile(path):
            logging.error(f"{label} not found: {path}")
            sys.exit(1)

    # Build config dict
    cfg = {
        "wrapper":        arg.wrapper,
        "infile":         os.path.abspath(arg.infile),
        "outdir":         os.path.abspath(arg.outdir),
        "replicates":     arg.replicates,
        "seed":           arg.seed,
        "threads":        arg.threads,
        "mainparams":     os.path.abspath(arg.mainparams) if arg.mainparams else None,
        "popfile":        os.path.abspath(arg.popfile)    if arg.popfile    else None,
        "indfile":        os.path.abspath(arg.indfile)    if arg.indfile    else None,
        "no_tests":       arg.no_tests,
        "no_plots":       arg.no_plots,
        "blacknwhite":    arg.blacknwhite,
        "use_ind_labels": arg.use_ind,
        "extra_opts":     arg.extra_opts,
        "fs_prior":       arg.fs_prior,
    }

    if arg.K is not None:
        cfg["K"] = arg.K
    else:
        cfg["K_list"] = arg.K_list

    if arg.structure_image:
        cfg["structure_image"] = arg.structure_image
    if arg.faststructure_image:
        cfg["faststructure_image"] = arg.faststructure_image

    # Write config
    os.makedirs(arg.outdir, exist_ok=True)
    config_path = os.path.join(os.path.abspath(arg.outdir),
                               ".structure_threader_config.yaml")
    with open(config_path, "w") as fh:
        yaml.dump(cfg, fh, default_flow_style=False)
    logging.info(f"Config written to: {config_path}")

    # Build Snakemake command
    cmd = [
        "snakemake",
        "--snakefile", arg.snakefile,
        "--configfile", config_path,
        "--cores", str(arg.threads),
        "--rerun-incomplete",
    ]

    if arg.use_singularity:
        cmd.append("--use-singularity")
        # Collect all host paths the container shell needs to reach
        bind_paths = set()
        bind_paths.add(os.path.dirname(os.path.abspath(arg.infile)))
        bind_paths.add(os.path.abspath(arg.outdir))
        if arg.mainparams:
            bind_paths.add(os.path.dirname(os.path.abspath(arg.mainparams)))
        if arg.popfile:
            bind_paths.add(os.path.dirname(os.path.abspath(arg.popfile)))
        if arg.indfile:
            bind_paths.add(os.path.dirname(os.path.abspath(arg.indfile)))
        cmd += ["--singularity-args", "--bind " + ",".join(sorted(bind_paths))]

    if arg.use_docker:
        cmd.append("--use-docker")
    if arg.use_conda:
        cmd.append("--use-conda")

    if arg.snakemake_args:
        cmd.extend(arg.snakemake_args.split())

    logging.info("Invoking Snakemake:\n  " + " ".join(cmd))
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def handle_plot(arg):
    try:
        import structure_threader.plotter.structplot as sp
    except ImportError:
        sys.path.insert(0, _SCRIPT_DIR)
        try:
            import plotter.structplot as sp
        except ImportError:
            logging.error("Could not import structure_threader.plotter.")
            sys.exit(1)

    results_path = os.path.abspath(arg.results_path)
    outpath      = os.path.abspath(arg.outpath)
    bestk        = [int(k) for k in arg.bestk]

    if arg.program == "structure":
        infiles = [os.path.join(results_path, f"str_K{k}_rep1_f") for k in bestk]
    elif arg.program == "faststructure":
        infiles = [os.path.join(results_path, f"fS_run_K.{k}.meanQ") for k in bestk]
    else:
        logging.error(f"plot for '{arg.program}' not yet ported.")
        sys.exit(1)

    for f in infiles:
        if not os.path.isfile(f):
            logging.error(f"Expected file not found: {f}")
            sys.exit(1)

    os.makedirs(outpath, exist_ok=True)
    sp.main(infiles, arg.program, outpath, bestk=bestk,
            popfile=arg.popfile, indfile=arg.indfile,
            bw=arg.blacknwhite, use_ind=arg.use_ind)
    logging.info("Plots generated successfully.")


def handle_params(arg):
    try:
        import structure_threader.skeletons.stparams as parameters
    except ImportError:
        sys.path.insert(0, _SCRIPT_DIR)
        try:
            import skeletons.stparams as parameters
        except ImportError:
            logging.error("Could not import structure_threader.skeletons.")
            sys.exit(1)

    os.makedirs(arg.outpath, exist_ok=True)
    for fname, content in [("mainparams",  parameters.MAINPARAMS),
                            ("extraparams", parameters.EXTRAPARAMS)]:
        path = os.path.join(arg.outpath, fname)
        with open(path, "w") as fh:
            fh.write(content)
        logging.info(f"Written: {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    arg = parser.parse_args()

    if arg.main_op == "run":
        handle_run(arg)
    elif arg.main_op == "plot":
        handle_plot(arg)
    elif arg.main_op == "params":
        handle_params(arg)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
