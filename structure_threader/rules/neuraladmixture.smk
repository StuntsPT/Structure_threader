# rules/neuraladmixture.smk
# Rules for running NeuralAdmixture (one job per K, or one job in supervised mode).
#
# NeuralAdmixture v1.6.7 CLI differences vs the original structure_threader wrapper:
#   - --threads N  is now REQUIRED (replaces --num_cpus)
#   - --num_gpus   still exists
#   - --seed       is optional (defaults to 42)
#   - --pops_path  replaces --populations_path for supervised mode
#   - --init_file  replaces --initialization
#   - --supervised flag is gone; supervision is triggered by --pops_path alone
#
# NeuralAdmixture constraints:
#   1. threads=1 passed to Snakemake scheduler — NAD uses --threads internally.
#   2. notests=True always — no bestK method exists.
#   3. exec_mode: "train" (default) or "infer".
#   4. VCF.GZ input: extracted to .vcf on the host before container jobs.
#   5. Unsupervised: OUTDIR/nad_K{k}/nad_K{k}.{k}.Q  (one job per K)
#   6. Supervised:   OUTDIR/nad_K{n}_supervised/nad_K{n}_supervised.{n}.Q
#      Plotting is skipped for supervised mode.


# ---------------------------------------------------------------------------
# Rule: prepare_neuraladmixture_input
# Extracts VCF.GZ → VCF on the host. No-op for other formats.
# ---------------------------------------------------------------------------

rule prepare_neuraladmixture_input:
    input:
        infile     = INFILE,
        dirs_ready = DIRS_SENTINEL,
    output:
        sentinel = NAD_INPUT_SENTINEL,
    run:
        import sys, logging
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)

        try:
            import structure_threader.wrappers.alstructure_wrapper as alsw
        except ImportError:
            _wf_dir = os.path.dirname(os.path.abspath(workflow.snakefile))
            sys.path.insert(0, _wf_dir)
            import wrappers.alstructure_wrapper as alsw

        if INFILE.endswith(".vcf.gz"):
            logging.info("Extracting VCF.GZ → VCF for NeuralAdmixture …")
            alsw.vcfgz_to_vcf(INFILE)
        else:
            logging.info("Input format does not require extraction.")

        with open(output.sentinel, "w") as fh:
            fh.write("ready\n")


# ---------------------------------------------------------------------------
# Rule: run_neuraladmixture  (unsupervised, one job per K)
# ---------------------------------------------------------------------------

if not NAD_SUPERVISED:
    rule run_neuraladmixture:
        input:
            infile      = NAD_INFILE,
            input_ready = NAD_INPUT_SENTINEL,
        output:
            qfile = os.path.join(OUTDIR, "nad_K{k}", "nad_K{k}.{k}.Q"),
        params:
            run_name   = lambda wc: f"nad_K{wc.k}",
            output_dir = lambda wc: os.path.join(OUTDIR, f"nad_K{wc.k}") + os.sep,
            exec_mode  = NAD_EXEC_MODE,
            seed       = NAD_SEED,
            threads    = NAD_THREADS,
            init_file  = NAD_INIT or "",
            gpus       = NAD_GPUS,
            bin        = WRAPPER_BIN,
        log:
            os.path.join(OUTDIR, "logs", "neuraladmixture_K{k}.log"),
        threads: 1   # Snakemake scheduler slot; NAD parallelism via --threads
        container:
            None if NO_CONTAINER else NEURALADMIXTURE_IMAGE
        shell:
            r"""
            CMD="{params.bin} {params.exec_mode} \
                 --name {params.run_name} \
                 --k {wildcards.k} \
                 --data_path {input.infile} \
                 --save_dir {params.output_dir} \
                 --seed {params.seed} \
                 --threads {params.threads}"

            if [ -n "{params.init_file}" ]; then
                CMD="$CMD --init_file {params.init_file}"
            fi

            if [ "{params.gpus}" -gt 0 ] 2>/dev/null; then
                CMD="$CMD --num_gpus {params.gpus}"
            fi

            echo "Running: $CMD" > {log}
            $CMD >> {log} 2>&1
            """


# ---------------------------------------------------------------------------
# Rule: run_neuraladmixture_supervised  (single job, K = n_populations)
# ---------------------------------------------------------------------------

else:
    rule run_neuraladmixture_supervised:
        input:
            infile      = NAD_INFILE,
            input_ready = NAD_INPUT_SENTINEL,
            popfile     = NAD_POPFILE,
        output:
            qfile = NAD_SUPERVISED_QFILE,
        params:
            run_name   = NAD_SUPERVISED_RUN_NAME,
            output_dir = NAD_SUPERVISED_OUTPUT_DIR,
            exec_mode  = NAD_EXEC_MODE,
            seed       = NAD_SEED,
            threads    = NAD_THREADS,
            init_file  = NAD_INIT or "",
            gpus       = NAD_GPUS,
            n_pops     = NAD_N_POPS,
            bin        = WRAPPER_BIN,
        log:
            os.path.join(OUTDIR, "logs", "neuraladmixture_supervised.log"),
        threads: 1
        container:
            None if NO_CONTAINER else NEURALADMIXTURE_IMAGE
        shell:
            r"""
            CMD="{params.bin} {params.exec_mode} \
                 --name {params.run_name} \
                 --k {params.n_pops} \
                 --data_path {input.infile} \
                 --save_dir {params.output_dir} \
                 --seed {params.seed} \
                 --threads {params.threads} \
                 --pops_path {input.popfile}"

            if [ -n "{params.init_file}" ]; then
                CMD="$CMD --init_file {params.init_file}"
            fi

            if [ "{params.gpus}" -gt 0 ] 2>/dev/null; then
                CMD="$CMD --num_gpus {params.gpus}"
            fi

            echo "Running: $CMD" > {log}
            $CMD >> {log} 2>&1
            """


# ---------------------------------------------------------------------------
# Rule: bestk_neuraladmixture
# No bestK method — write all tested K values (or supervised K) as sentinel.
# ---------------------------------------------------------------------------

rule bestk_neuraladmixture:
    input:
        qfiles = all_nad_qfiles(),
    output:
        sentinel = bestk_sentinel(),
    run:
        import logging
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)
        logging.info("NeuralAdmixture has no bestK method — "
                     "using all tested K values.")
        os.makedirs(os.path.dirname(output.sentinel), exist_ok=True)
        bestk = [NAD_N_POPS] if NAD_SUPERVISED else K_LIST
        with open(output.sentinel, "w") as fh:
            fh.write("\n".join(str(k) for k in bestk) + "\n")


# ---------------------------------------------------------------------------
# Rule: cleanup_neuraladmixture_input
# Removes extracted .vcf after all runs (only when input was .vcf.gz).
# ---------------------------------------------------------------------------

if INFILE.endswith(".vcf.gz"):
    rule cleanup_neuraladmixture_input:
        input:
            qfiles = all_nad_qfiles(),
        output:
            sentinel = os.path.join(OUTDIR, ".neuraladmixture_cleanup_done"),
        run:
            import logging
            logging.basicConfig(format="%(levelname)s: %(message)s",
                                level=logging.INFO)
            extracted_vcf = INFILE[:-3]
            if os.path.exists(extracted_vcf):
                os.remove(extracted_vcf)
                logging.info(f"Removed extracted VCF: {extracted_vcf}")
            with open(output.sentinel, "w") as fh:
                fh.write("done\n")
