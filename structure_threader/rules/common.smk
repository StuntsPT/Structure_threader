# rules/common.smk
# Shared rules used by all wrappers:
#   - prepare_dirs  : creates output directories on the host before any
#                     container jobs run (Apptainer bind-mount targets must
#                     exist before the container starts)
#   - bestk         : runs the appropriate bestK method for the active wrapper
#   - plot          : runs structplot for the active wrapper


# ---------------------------------------------------------------------------
# Rule: prepare_dirs
# Creates OUTDIR and OUTDIR/logs on the host.  All container rules depend on
# this sentinel so directories are guaranteed to exist before any bind-mount.
# ---------------------------------------------------------------------------

rule prepare_dirs:
    output:
        sentinel = DIRS_SENTINEL,
    run:
        os.makedirs(OUTDIR, exist_ok=True)
        os.makedirs(os.path.join(OUTDIR, "logs"), exist_ok=True)
        os.makedirs(os.path.join(OUTDIR, "bestK"), exist_ok=True)
        os.makedirs(os.path.join(OUTDIR, "plots"), exist_ok=True)
        with open(output.sentinel, "w") as fh:
            fh.write("ready\n")


# ---------------------------------------------------------------------------
# Rule: bestk
# Dispatches to the correct bestK method based on WRAPPER.
# ---------------------------------------------------------------------------

rule bestk:
    input:
        # Aggregates all primary outputs, whichever wrapper produced them
        files = (all_structure_f_files() if WRAPPER == "structure"
                 else all_fs_meanq_files()),
    output:
        sentinel = bestk_sentinel(),
    params:
        resultsdir = OUTDIR,
        outdir     = os.path.join(OUTDIR, "bestK"),
    log:
        os.path.join(OUTDIR, "logs", "bestk.log"),
    run:
        import sys, logging
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)
        os.makedirs(params.outdir, exist_ok=True)

        try:
            import structure_threader.evanno.structureHarvester as sh
            import structure_threader.evanno.harvesterCore as hc
            import structure_threader.evanno.fastChooseK as fck
        except ImportError:
            _wf_dir = os.path.dirname(os.path.abspath(workflow.snakefile))
            sys.path.insert(0, _wf_dir)
            import evanno.structureHarvester as sh
            import evanno.harvesterCore as hc
            import evanno.fastChooseK as fck

        if WRAPPER == "structure":
            logging.info("Inferring optimal K using the Evanno method …")
            data = hc.Data()
            sh.harvestFiles(data, params.resultsdir)
            hc.calculateMeansAndSds(data)
            # evannoMethod() populates data.deltaK via calculatePrimesDoublePrimesDeltaK
            # but discards the bk return value from writeEvannoTableToFile.
            # We call evannoMethod() for its side-effects, then capture bk ourselves.
            sh.evannoMethod(data, params.outdir)
            bestk = sh.writeEvannoTableToFile(data, params.outdir)
            hc.writeRawOutputToFile(os.path.join(params.outdir, "summary.txt"), data)

        elif WRAPPER == "faststructure":
            logging.info("Inferring optimal K using fastChooseK …")
            # fastChooseK.main() globs *.log and *.meanQ from the results dir
            bestk = fck.main(params.resultsdir, params.outdir)

        logging.info(f"Best K: {bestk}")
        with open(output.sentinel, "w") as fh:
            fh.write("\n".join(str(k) for k in bestk) + "\n")


# ---------------------------------------------------------------------------
# Rule: plot
# Runs structplot for the active wrapper.
# ---------------------------------------------------------------------------

rule plot:
    input:
        files   = (all_structure_f_files() if WRAPPER == "structure"
                   else all_fs_meanq_files()),
        bestk_f = bestk_sentinel() if not NO_TESTS else [],
    output:
        sentinel = plot_sentinel(),
    params:
        outdir  = os.path.join(OUTDIR, "plots"),
        popfile = POPFILE,
        indfile = INDFILE,
        bw      = BW,
        use_ind = USE_IND,
    log:
        os.path.join(OUTDIR, "logs", "plot.log"),
    run:
        import sys, logging
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)
        os.makedirs(params.outdir, exist_ok=True)

        try:
            import structure_threader.plotter.structplot as sp
        except ImportError:
            _wf_dir = os.path.dirname(os.path.abspath(workflow.snakefile))
            sys.path.insert(0, _wf_dir)
            import plotter.structplot as sp

        # Determine bestk list
        _bestk_f = (input.bestk_f[0] if isinstance(input.bestk_f, list)
                    else input.bestk_f)
        if not NO_TESTS and os.path.exists(_bestk_f):
            with open(_bestk_f) as fh:
                bestk = [int(l.strip()) for l in fh if l.strip()]
        else:
            bestk = K_LIST

        if WRAPPER == "structure":
            # One representative replicate per K (rep 1)
            plt_files = [os.path.join(OUTDIR, f"str_K{k}_rep1_f")
                         for k in K_LIST]
        elif WRAPPER == "faststructure":
            plt_files = [os.path.join(OUTDIR, f"fS_run_K.{k}.meanQ")
                         for k in K_LIST]

        logging.info("Drawing admixture plots …")
        sp.main(
            plt_files,
            WRAPPER,          # "structure" or "faststructure"
            params.outdir,
            bestk   = bestk,
            popfile = params.popfile,
            indfile = params.indfile,
            bw      = params.bw,
            use_ind = params.use_ind,
        )
        logging.info("Plots done.")

        with open(output.sentinel, "w") as fh:
            fh.write("done\n")
