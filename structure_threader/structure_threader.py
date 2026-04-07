#!/usr/bin/env python3
"""
structure_threader  —  Snakemake-based wrapper for population structure programs.

Usage examples:

  # STRUCTURE — containerised
  structure_threader run -st -K 6 -R 10 -i data/mydata.str -o results/ \\
      --params data/mainparams -t 8 --use-singularity

  # fastSTRUCTURE — containerised
  structure_threader run -fs -K 6 -i data/mydata.str -o results/ \\
      --pop data/pops.txt -t 8 --use-singularity

  # MavericK — containerised
  structure_threader run -mv -K 6 -i data/mydata.str -o results/ \\
      --params data/parameters.txt -t 8 --use-singularity

  # Re-plot from existing results
  structure_threader plot -i results/ -f structure -K 3 -o results/plots/ \\
      --pop data/populations.txt

  # Generate STRUCTURE skeleton parameter files
  structure_threader params -o data/
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
_PORTED = {"structure", "faststructure", "maverick", "alstructure", "neuraladmixture"}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="structure_threader",
        description="structure_threader — Snakemake edition.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subs = parser.add_subparsers(dest="main_op",
                                 help="Select operation to perform.")

    # ── run ────────────────────────────────────────────────────────────────
    run = subs.add_parser("run", help="Perform a full run.")

    io = run.add_argument_group("Input / Output")
    io.add_argument("-i",       dest="infile",     required=True, metavar="FILE",
                    help="Input file.")
    io.add_argument("-o",       dest="outdir",     required=True, metavar="DIR",
                    help="Output directory.")
    io.add_argument("--params", dest="params",     default=None,  metavar="FILE",
                    help="Parameter file (mainparams for STRUCTURE, "
                         "parameters.txt for MavericK).")

    prog = run.add_argument_group("Wrapped program (mutually exclusive)")
    prog_ex = prog.add_mutually_exclusive_group(required=True)
    # These flags identify the wrapper. An optional binary path may follow each
    # flag (e.g. -st /usr/local/bin/structure); it is extracted from sys.argv
    # in handle_run() and used only when --no-container is active.
    prog_ex.add_argument("-st",  dest="wrapper", action="store_const",
                         const="structure",
                         help="Wrap STRUCTURE. Optionally follow with binary path "
                              "for --no-container mode.")
    prog_ex.add_argument("-fs",  dest="wrapper", action="store_const",
                         const="faststructure",
                         help="Wrap fastSTRUCTURE. Optionally follow with binary path.")
    prog_ex.add_argument("-mv",  dest="wrapper", action="store_const",
                         const="maverick",
                         help="Wrap MavericK. Optionally follow with binary path.")
    prog_ex.add_argument("-als", dest="wrapper", action="store_const",
                         const="alstructure",
                         help="Wrap ALStructure. Optionally follow with Rscript path.")
    prog_ex.add_argument("-nad", dest="wrapper", action="store_const",
                         const="neuraladmixture",
                         help="Wrap NeuralAdmixture. Optionally follow with binary path.")

    # ── post-parse wrapper normalisation is done in handle_run ──────────────

    k = run.add_argument_group("K options (provide exactly one)")
    k_ex = k.add_mutually_exclusive_group(required=True)
    k_ex.add_argument("-K",     dest="K",      type=int,       metavar="INT",
                      help="Run K=1…K.")
    k_ex.add_argument("-Klist", dest="K_list", nargs="+", type=int, metavar="INT",
                      help="Explicit list of K values.")

    ro = run.add_argument_group("Run options")
    ro.add_argument("-R",           dest="replicates", type=int, default=20,
                    metavar="INT",
                    help="Replicates per K [STRUCTURE only, default: 20].")
    ro.add_argument("-t",           dest="threads",    type=int, default=4,
                    metavar="INT",
                    help="Parallel jobs / Snakemake --cores (default: 4).")
    ro.add_argument("--seed",       dest="seed",       type=int, default=1235813,
                    metavar="INT")
    ro.add_argument("--extra_opts", dest="extra_opts", default="", metavar="STR",
                    help="Extra flags passed verbatim to the wrapped program.")
    ro.add_argument("--prior",      dest="fs_prior",   default="simple",
                    choices=["simple", "logistic"],
                    help="fastSTRUCTURE prior (default: simple).")
    ro.add_argument("--exec_mode",  dest="nad_exec_mode", default="train",
                    choices=["train", "infer"],
                    help="NeuralAdmixture execution mode (default: train).")
    ro.add_argument("--supervised", dest="nad_supervised", action="store_true",
                    help="Run NeuralAdmixture in supervised mode.")
    ro.add_argument("--nad_pop",    dest="nad_popfile", default=None, metavar="FILE",
                    help="Population file for supervised NeuralAdmixture.")
    ro.add_argument("--init",       dest="nad_init", default=None, metavar="STR",
                    help="NeuralAdmixture initialization method.")
    ro.add_argument("--nad_threads", dest="nad_threads", type=int, default=1, metavar="INT",
                    help="Threads for NeuralAdmixture --threads (required by NAD, default: 1).")
    ro.add_argument("--nad_gpus",   dest="nad_gpus", type=int, default=0, metavar="INT",
                    help="GPUs for NeuralAdmixture (default: 0 = CPU only).")
    ro.add_argument("--nad_seed",   dest="nad_seed", type=int, default=1235813, metavar="INT",
                    help="NeuralAdmixture random seed (default: 1235813).")

    ids = run.add_argument_group("Individual / Population labels")
    ids_ex = ids.add_mutually_exclusive_group()
    ids_ex.add_argument("--pop", dest="popfile", default=None, metavar="FILE")
    ids_ex.add_argument("--ind", dest="indfile", default=None, metavar="FILE")

    pl = run.add_argument_group("Analysis / plot options")
    pl.add_argument("--no_tests",       dest="no_tests",    action="store_true",
                    help="Skip bestK estimation.")
    pl.add_argument("--no_plots",       dest="no_plots",    action="store_true",
                    help="Skip plot generation.")
    pl.add_argument("--no_clumpp",      dest="no_clumpp",   action="store_true",
                    help="Skip Clumppling alignment.")
    pl.add_argument("--clumppling_plot_type", dest="clumppling_plot_type",
                    default="graph",
                    choices=["graph", "list", "withinK", "major", "all"],
                    help="Clumppling plot type (default: graph).")
    pl.add_argument("--clumppling_fig_format", dest="clumppling_fig_format",
                    default="svg",
                    help="Clumppling figure format (default: svg).")
    pl.add_argument("--clumppling_cd_method", dest="clumppling_cd_method",
                    default="louvain",
                    choices=["louvain", "leiden", "infomap",
                             "markov_clustering", "label_propagation",
                             "walktrap", "custom"],
                    help="Clumppling community detection method (default: louvain).")
    pl.add_argument("--clumppling_cd_res", dest="clumppling_cd_res",
                    type=float, default=1.0, metavar="FLOAT",
                    help="Clumppling CD resolution parameter (default: 1.0).")
    pl.add_argument("--clumppling_image", dest="clumppling_image",
                    default=None, metavar="URI",
                    help="Override the Clumppling container image URI.")
    pl.add_argument("-bw",              dest="blacknwhite", action="store_true",
                    help="Greyscale plots.")
    pl.add_argument("--use-ind-labels", dest="use_ind",     action="store_true",
                    help="Label individuals rather than populations.")

    sm = run.add_argument_group("Snakemake / container options")
    sm.add_argument("--use-singularity",     dest="use_singularity",
                    action="store_true",
                    help="Run rules inside Singularity/Apptainer containers "
                         "(auto-enabled when apptainer/singularity is detected).")
    sm.add_argument("--no-container",        dest="no_container",
                    action="store_true",
                    help="Disable containers and use local binaries instead. "
                         "Binary paths can be passed after each wrapper flag "
                         "(e.g. -st /usr/local/bin/structure).")
    sm.add_argument("--use-docker",          dest="use_docker",
                    action="store_true",
                    help="Run rules inside Docker containers.")
    sm.add_argument("--use-conda",           dest="use_conda",
                    action="store_true",
                    help="Use per-rule conda environments.")
    sm.add_argument("--snakefile",           dest="snakefile",
                    default=_DEFAULT_SNAKEFILE, metavar="FILE")
    sm.add_argument("--snakemake-args",      dest="snakemake_args",
                    default="", metavar="STR",
                    help="Extra arguments forwarded verbatim to Snakemake.")
    sm.add_argument("--structure-image",     dest="structure_image",
                    default=None, metavar="URI")
    sm.add_argument("--faststructure-image", dest="faststructure_image",
                    default=None, metavar="URI")
    sm.add_argument("--maverick-image",      dest="maverick_image",
                    default=None, metavar="URI")
    sm.add_argument("--alstructure-image",   dest="alstructure_image",
                    default=None, metavar="URI")
    sm.add_argument("--neuraladmixture-image", dest="neuraladmixture_image",
                    default=None, metavar="URI")

    # ── plot ───────────────────────────────────────────────────────────────
    plot = subs.add_parser("plot", help="Re-draw plots from existing results.")
    pm = plot.add_argument_group("Main options")
    pm.add_argument("-i", dest="results_path", required=True,  metavar="DIR")
    pm.add_argument("-f", dest="program",      required=True,
                   choices=["structure", "faststructure", "maverick",
                             "alstructure", "neuraladmixture"])
    pm.add_argument("-K", dest="bestk",        required=True, nargs="+",
                   metavar="INT")
    pm.add_argument("-o", dest="outpath",      default=".", metavar="DIR")
    pe = plot.add_argument_group("Extra options")
    pe.add_argument("-bw",              dest="blacknwhite", action="store_true")
    pe.add_argument("--use-ind-labels", dest="use_ind",     action="store_true")
    ps = plot.add_argument_group("Sorting (provide one)")
    ps_ex = ps.add_mutually_exclusive_group(required=True)
    ps_ex.add_argument("--pop", dest="popfile", default=None, metavar="FILE")
    ps_ex.add_argument("--ind", dest="indfile", default=None, metavar="FILE")

    # ── params ─────────────────────────────────────────────────────────────
    params_cmd = subs.add_parser(
        "params", help="Generate skeleton STRUCTURE parameter files.")
    params_cmd.add_argument("-o", dest="outpath", required=True, metavar="DIR")

    return parser


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def handle_run(arg):
    # Detect wrapper and extract optional binary path from sys.argv.
    # The flag identifies the wrapper; the next token (if it doesn't start
    # with '-') is treated as the binary path for --no-container mode.
    _FLAG_TO_WRAPPER = {
        "-st": "structure", "-fs": "faststructure", "-mv": "maverick",
        "-als": "alstructure", "-nad": "neuraladmixture",
    }
    binary_path = None
    for flag, name in _FLAG_TO_WRAPPER.items():
        if flag in sys.argv:
            idx = sys.argv.index(flag)
            if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("-"):
                binary_path = sys.argv[idx + 1]
                if not arg.no_container:
                    logging.warning(
                        f"Binary path '{binary_path}' passed to {flag} — "
                        "ignored (using container). Pass --no-container to "
                        "use local binaries."
                    )
            break

    if arg.wrapper not in _PORTED:
        logging.error(
            f"Wrapper '{arg.wrapper}' is not yet ported to the Snakemake "
            f"edition.\nAvailable: {', '.join(sorted(_PORTED))}.\n"
            "Use the original structure_threader for other wrappers."
        )
        sys.exit(1)

    # Wrapper-specific validation
    if arg.wrapper == "faststructure" and not arg.popfile and not arg.indfile:
        logging.error("-fs requires either --pop or --ind.")
        sys.exit(1)
    if arg.wrapper == "maverick" and not arg.params:
        logging.error("-mv requires --params (MavericK parameters file).")
        sys.exit(1)
    if arg.wrapper == "neuraladmixture" and arg.nad_supervised and not arg.nad_popfile:
        logging.error("--supervised requires --nad_pop (population file).")
        sys.exit(1)
    if arg.wrapper == "alstructure":
        # K=1 is unsupported by ALStructure; strip it with a warning
        k_list = arg.K_list if arg.K_list else list(range(1, arg.K + 1))
        if 1 in k_list:
            logging.warning("ALStructure cannot run K=1 — removing it from the K list.")
        # The Snakefile also strips K=1, but we update K/K_list here so the
        # config reflects what will actually run.
        k_list = [k for k in k_list if k != 1]
        if not k_list:
            logging.error("No valid K values after removing K=1.")
            sys.exit(1)
        if arg.K_list:
            arg.K_list = k_list
        else:
            # Express as K_list so the exact values are preserved
            arg.K_list = k_list
            arg.K = None

    # File existence checks
    checks = [("infile", arg.infile)]
    if arg.params:
        checks.append(("params", arg.params))
    if arg.popfile:
        checks.append(("popfile", arg.popfile))
    if arg.indfile:
        checks.append(("indfile", arg.indfile))
    for label, path in checks:
        if not os.path.isfile(path):
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
        "popfile":        os.path.abspath(arg.popfile) if arg.popfile else None,
        "indfile":        os.path.abspath(arg.indfile) if arg.indfile else None,
        "no_tests":       arg.no_tests,
        "no_plots":       arg.no_plots,
        "no_clumpp":      arg.no_clumpp,
        "clumppling_plot_type":   arg.clumppling_plot_type,
        "clumppling_fig_format":  arg.clumppling_fig_format,
        "clumppling_cd_method":   arg.clumppling_cd_method,
        "clumppling_cd_res":      arg.clumppling_cd_res,
        "blacknwhite":    arg.blacknwhite,
        "use_ind_labels": arg.use_ind,
        "extra_opts":     arg.extra_opts,
        # Binary path for --no-container mode. None when using containers.
        "wrapper_bin":    binary_path,
        "no_container":   arg.no_container,
        "fs_prior":       arg.fs_prior,
        "nad_exec_mode":  arg.nad_exec_mode,
        "nad_supervised": arg.nad_supervised,
        "nad_popfile":    os.path.abspath(arg.nad_popfile) if arg.nad_popfile else None,
        "nad_init":       arg.nad_init,
        "nad_threads":    arg.nad_threads,
        "nad_gpus":       arg.nad_gpus,
        "nad_seed":       arg.nad_seed,
        # Wrapper-specific params file — stored under its own key so both
        # STRUCTURE mainparams and MavericK parameters.txt can coexist.
        "mainparams":     (os.path.abspath(arg.params)
                           if arg.params and arg.wrapper == "structure"
                           else None),
        "mav_params":     (os.path.abspath(arg.params)
                           if arg.params and arg.wrapper == "maverick"
                           else None),
    }

    if arg.K is not None:
        cfg["K"] = arg.K
    else:
        cfg["K_list"] = arg.K_list

    for attr, key in [("structure_image",     "structure_image"),
                      ("faststructure_image", "faststructure_image"),
                      ("maverick_image",      "maverick_image"),
                      ("alstructure_image",  "alstructure_image"),
                      ("neuraladmixture_image", "neuraladmixture_image"),
                      ("clumppling_image",      "clumppling_image")]:
        val = getattr(arg, attr, None)
        if val:
            cfg[key] = val

    # ── Container runtime auto-detection (must run BEFORE writing config) ────────────────
    # We need to know whether containers are active so that wrapper_bin is
    # correctly nulled out in the config when running inside a container
    # (the binary lives on the container's PATH, not on the host path).
    if arg.no_container:
        # Explicit opt-out: use local binaries.
        logging.info("Container mode disabled — using local binaries.")
    elif arg.use_singularity or arg.use_docker or arg.use_conda:
        pass   # user made an explicit container choice; honour it below
    else:
        # Auto-detect: enable Singularity/Apptainer if available
        import shutil as _shutil
        if _shutil.which("apptainer") or _shutil.which("singularity"):
            logging.info(
                "Container runtime detected — enabling Singularity automatically. "
                "Pass --no-container to use local binaries instead."
            )
            arg.use_singularity = True
        else:
            logging.warning(
                "No container runtime found (apptainer/singularity/docker). "
                "Falling back to local binaries — ensure wrapped programs are "
                "on PATH, or install a container runtime."
            )

    # When running in container mode, any host binary path the user supplied
    # after the wrapper flag (e.g. -nad /usr/bin/neural-admixture) must NOT
    # be forwarded to the Snakemake rules — the binary is on the container's
    # PATH and the host path is meaningless (and likely absent) inside it.
    # Setting wrapper_bin to None lets the Snakefile fall back to the bare
    # default name from _DEFAULT_BINS (e.g. "neural-admixture").
    using_container = (arg.use_singularity or arg.use_docker) and not arg.no_container
    if using_container:
        cfg["wrapper_bin"] = None

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
        bind_paths = set()
        bind_paths.add(os.path.dirname(os.path.abspath(arg.infile)))
        bind_paths.add(os.path.abspath(arg.outdir))
        if arg.params:
            bind_paths.add(os.path.dirname(os.path.abspath(arg.params)))
        if arg.popfile:
            bind_paths.add(os.path.dirname(os.path.abspath(arg.popfile)))
        if arg.indfile:
            bind_paths.add(os.path.dirname(os.path.abspath(arg.indfile)))
        if arg.wrapper == "neuraladmixture" and arg.nad_popfile:
            bind_paths.add(os.path.dirname(os.path.abspath(arg.nad_popfile)))
        if arg.wrapper == "alstructure":
            # The bundled alstructure_wrapper.R must be reachable inside the
            # container. Bind-mount the wrappers/ directory from the repo.
            wrappers_dir = os.path.join(
                os.path.dirname(os.path.abspath(arg.snakefile)), "wrappers"
            )
            if os.path.isdir(wrappers_dir):
                bind_paths.add(wrappers_dir)
        cmd += ["--singularity-args", "--bind " + ",".join(sorted(bind_paths))]

    if arg.use_docker:
        cmd.append("--use-docker")
    if arg.use_conda:
        cmd.append("--use-conda")
    if arg.snakemake_args:
        cmd.extend(arg.snakemake_args.split())

    logging.info("Invoking Snakemake:\n  " + " ".join(cmd))
    sys.exit(subprocess.run(cmd).returncode)


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
        infiles = [os.path.join(results_path, f"str_K{k}_rep1_f")
                   for k in bestk]
    elif arg.program == "faststructure":
        infiles = [os.path.join(results_path, f"fS_run_K.{k}.meanQ")
                   for k in bestk]
    elif arg.program == "maverick":
        infiles = [os.path.join(results_path, f"mav_K{k}",
                                f"outputQmatrix_ind_K{k}.csv")
                   for k in bestk]
    elif arg.program == "alstructure":
        infiles = [os.path.join(results_path, f"alstr_K{k}")
                   for k in bestk]
    elif arg.program == "neuraladmixture":
        infiles = [os.path.join(results_path, f"nad_K{k}", f"nad_K{k}.{k}.Q")
                   for k in bestk]
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
    arg, _ = parser.parse_known_args()  # unknown args = binary paths after flags

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
