# rules/alstructure.smk
# Rules for running ALStructure (one job per K value, no replicates).
#
# ALStructure has several important constraints that differ from other wrappers:
#
#   1. threads=1 is forced — the R dependency installer runs sequentially and
#      cannot be parallelised safely.
#
#   2. notests=True is always the case — there is no bestK estimation method
#      for ALStructure. bestk_alstructure writes all tested K values as the
#      sentinel so downstream rules behave consistently.
#
#   3. K=1 is excluded — ALStructure cannot model K=1. Already stripped from
#      K_LIST in the Snakefile when WRAPPER == "alstructure".
#
#   4. Output is a single CSV file at OUTDIR/alstr_K{k} (no extension).
#      R script signature: Rscript <script> <infile> <k> <outfile_stem>
#
#   5. VCF/VCF.GZ input is converted to TSV on the host in
#      prepare_alstructure_input before the container jobs start.
#      ALS_RSCRIPT_INFILE and ALS_TSV_TO_CLEAN are resolved in the Snakefile.


# ---------------------------------------------------------------------------
# Rule: prepare_alstructure_input
# Converts VCF/VCF.GZ → TSV matrix on the host. No-op for other formats.
# ---------------------------------------------------------------------------

rule prepare_alstructure_input:
    input:
        infile     = INFILE,
        dirs_ready = DIRS_SENTINEL,
    output:
        sentinel = ALS_INPUT_SENTINEL,
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
            logging.info("Extracting VCF.GZ → VCF …")
            extracted = alsw.vcfgz_to_vcf(INFILE)
            logging.info("Converting VCF → TSV matrix …")
            alsw.vcf_to_matrix(extracted)
        elif INFILE.endswith(".vcf"):
            logging.info("Converting VCF → TSV matrix …")
            alsw.vcf_to_matrix(INFILE)
        else:
            logging.info("Input format does not require conversion.")

        with open(output.sentinel, "w") as fh:
            fh.write("ready\n")


# ---------------------------------------------------------------------------
# Rule: run_alstructure
# One containerised R job per K value, run sequentially (threads=1).
# ---------------------------------------------------------------------------

rule run_alstructure:
    input:
        infile      = INFILE,
        input_ready = ALS_INPUT_SENTINEL,
        wrapper_r   = ALS_WRAPPER_R,   # bind-mounted from the repo into the container
    output:
        qfile = os.path.join(OUTDIR, "alstr_K{k}"),
    params:
        rscript_infile = ALS_RSCRIPT_INFILE,
        output_stem    = lambda wc: os.path.join(OUTDIR, f"alstr_K{wc.k}"),
        bin         = WRAPPER_BIN,
    log:
        os.path.join(OUTDIR, "logs", "alstructure_K{k}.log"),
    threads: 1
    container:
        None if NO_CONTAINER else ALSTRUCTURE_IMAGE
    shell:
        r"""
        echo "Running: {params.bin} {input.wrapper_r} {params.rscript_infile} {wildcards.k} {params.output_stem}" > {log}
        {params.bin} {input.wrapper_r} \
            {params.rscript_infile} \
            {wildcards.k} \
            {params.output_stem} >> {log} 2>&1
        """


# ---------------------------------------------------------------------------
# Rule: bestk_alstructure
# No bestK method for ALStructure — write all tested K values as sentinel.
# ---------------------------------------------------------------------------

rule bestk_alstructure:
    input:
        qfiles = all_als_qfiles(),
    output:
        sentinel = bestk_sentinel(),
    run:
        import logging
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)
        logging.info("ALStructure has no bestK method — "
                     "using all tested K values.")
        os.makedirs(os.path.dirname(output.sentinel), exist_ok=True)
        with open(output.sentinel, "w") as fh:
            fh.write("\n".join(str(k) for k in K_LIST) + "\n")


# ---------------------------------------------------------------------------
# Rule: cleanup_alstructure_input
# Removes intermediate TSV (and extracted VCF for .vcf.gz) after all runs.
# Only defined when VCF input required conversion.
# ---------------------------------------------------------------------------

if ALS_TSV_TO_CLEAN:
    rule cleanup_alstructure_input:
        input:
            qfiles = all_als_qfiles(),
        output:
            sentinel = os.path.join(OUTDIR, ".alstructure_cleanup_done"),
        run:
            import logging
            logging.basicConfig(format="%(levelname)s: %(message)s",
                                level=logging.INFO)
            if os.path.exists(ALS_TSV_TO_CLEAN):
                os.remove(ALS_TSV_TO_CLEAN)
                logging.info(f"Removed intermediate TSV: {ALS_TSV_TO_CLEAN}")
            if INFILE.endswith(".vcf.gz"):
                extracted_vcf = INFILE[:-3]
                if os.path.exists(extracted_vcf):
                    os.remove(extracted_vcf)
                    logging.info(f"Removed extracted VCF: {extracted_vcf}")
            with open(output.sentinel, "w") as fh:
                fh.write("done\n")
