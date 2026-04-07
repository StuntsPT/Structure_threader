# rules/maverick.smk
# Rules for running MavericK (one job per K value, no replicates).
#
# MavericK differs from STRUCTURE and fastSTRUCTURE in one important way:
# the post-processing step (maverick_merger) is BOTH the aggregation step
# AND the bestK computation. It subsumes the generic bestk rule entirely.
# The DAG is therefore:
#
#   prepare_dirs → run_maverick (K parallel jobs)
#                      └─► merge_maverick  (aggregates all K outputs,
#                                           computes TI/STRUCTURE bestK,
#                                           writes bestK sentinel)
#                                  └─► plot  (via common.smk)
#
# The generic bestk rule in common.smk is skipped for MavericK because
# the Snakefile only requests bestk_sentinel() when WRAPPER != "maverick".


# ---------------------------------------------------------------------------
# Rule: run_maverick
# One containerised job per K value.  MavericK is single-threaded internally
# but uses MainRepeats (set in the parameters file) for within-K repetitions.
# ---------------------------------------------------------------------------

rule run_maverick:
    input:
        infile     = INFILE,
        dirs_ready = DIRS_SENTINEL,
        params_f   = MAV_PARAMS,          # mandatory for MavericK
    output:
        # MavericK writes outputQmatrix_ind_K{k}.csv (and many other files)
        # into outdir/mav_K{k}/.  We declare only the Q-matrix file that
        # downstream rules need; everything else is a side-effect.
        qmatrix = os.path.join(OUTDIR, "mav_K{k}",
                               "outputQmatrix_ind_K{k}.csv"),
    params:
        output_dir  = lambda wc: os.path.join(OUTDIR,
                                               f"mav_K{wc.k}") + os.sep,
        no_tests    = NO_TESTS,
        # Alpha failsafe: if alpha/alphaPropSD are comma-separated in the
        # params file we pass the per-K value on the CLI.
        alpha_args  = lambda wc: _mav_alpha_args(int(wc.k)),
        bin         = WRAPPER_BIN,
    log:
        os.path.join(OUTDIR, "logs", "maverick_K{k}.log"),
    threads: 1
    container:
        None if NO_CONTAINER else MAVERICK_IMAGE
    shell:
        r"""
        mkdir -p {params.output_dir}

        CMD="{params.bin} \
             -Kmin {wildcards.k} \
             -Kmax {wildcards.k} \
             -data {input.infile} \
             -outputRoot {params.output_dir} \
             -masterRoot / \
             -parameters {input.params_f}"

        if [ "{params.no_tests}" = "True" ]; then
            CMD="$CMD -thermodynamic_on f"
        fi

        if [ -n "{params.alpha_args}" ]; then
            CMD="$CMD {params.alpha_args}"
        fi

        echo "Running: $CMD" > {log}
        $CMD >> {log} 2>&1
        """


# ---------------------------------------------------------------------------
# Rule: merge_maverick
# Aggregates all per-K MavericK outputs, runs TI/STRUCTURE normalisation,
# determines bestK, and writes the sentinel file that plot depends on.
# This rule replaces the generic bestk rule for MavericK.
# ---------------------------------------------------------------------------

rule merge_maverick:
    input:
        qmatrices = [os.path.join(OUTDIR, f"mav_K{k}",
                                  f"outputQmatrix_ind_K{k}.csv")
                     for k in K_LIST],
    output:
        sentinel = bestk_sentinel(),
    params:
        outdir    = OUTDIR,
        params_f  = MAV_PARAMS,
        no_tests  = NO_TESTS,
    log:
        os.path.join(OUTDIR, "logs", "merge_maverick.log"),
    run:
        import sys, logging
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)

        try:
            import structure_threader.wrappers.maverick_wrapper as mw
        except ImportError:
            _wf_dir = os.path.dirname(os.path.abspath(workflow.snakefile))
            sys.path.insert(0, _wf_dir)
            import wrappers.maverick_wrapper as mw

        logging.info("Merging MavericK outputs and computing bestK …")
        mav_params = mw.mav_params_parser(params.params_f)
        bestk = mw.maverick_merger(params.outdir, K_LIST, mav_params,
                                   params.no_tests)

        # maverick_merger returns None when no_tests=True (no TI output)
        if bestk is None:
            bestk = K_LIST

        logging.info(f"Best K: {bestk}")
        os.makedirs(os.path.dirname(output.sentinel), exist_ok=True)
        with open(output.sentinel, "w") as fh:
            fh.write("\n".join(str(k) for k in bestk) + "\n")
