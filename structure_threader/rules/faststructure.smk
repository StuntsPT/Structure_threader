# rules/faststructure.smk
# Rule for running fastSTRUCTURE (one job per K value, no replicates).
#
# Key differences from STRUCTURE:
#   - No replicates: fastSTRUCTURE is a variational method; one run per K suffices.
#   - Output naming: fastSTRUCTURE writes fS_run_K.{K}.meanQ / .varQ / .log
#     to the output directory, using the common stem set in fs_cli_generator.
#   - Input format: accepts .bed/.fam/.bim (PLINK) or .str (STR format).
#     If the input file is not already .str, fastSTRUCTURE needs a symlink.
#     We handle this in the shell block.
#   - Seed: passed via --seed.
#   - Prior: "simple" (default) or "logistic", passed via --prior.
#   - The binary inside the biocontainers image is called `fastStructure`
#     (not python2 structure.py) — the image already wraps the Python 2 call.
#
# bestk and plot are in rules/common.smk.


rule run_faststructure:
    input:
        infile     = INFILE,
        dirs_ready = DIRS_SENTINEL,
    output:
        # fastSTRUCTURE writes {stem}.{K}.meanQ, .varQ, .log
        # We declare meanQ as the primary output; bestk and plot use it.
        meanq = os.path.join(OUTDIR, "fS_run_K.{k}.meanQ"),
    params:
        # Output stem: fastSTRUCTURE appends .{K}.{ext} to this
        output_stem = os.path.join(OUTDIR, "fS_run_K"),
        prior       = FS_PRIOR,
        seed        = SEED,
        extra       = config.get("extra_opts", ""),
        bin         = WRAPPER_BIN,
        # We need the infile without extension for STR format
        # (fastSTRUCTURE appends .str itself when using --format str)
        infile_stem = lambda wc: (
            INFILE[:-4] if INFILE.endswith(".str") else
            INFILE[:-4] if INFILE.endswith((".bed", ".fam", ".bim")) else
            INFILE
        ),
        use_bed = INFILE.endswith((".bed", ".fam", ".bim")),
    log:
        os.path.join(OUTDIR, "logs", "faststructure_K{k}.log"),
    threads: 1
    container:
        None if NO_CONTAINER else FASTSTRUCTURE_IMAGE
    shell:
        r"""
        # Determine format flag
        if [ "{params.use_bed}" = "True" ]; then
            FMT="bed"
            INFILE_ARG="{params.infile_stem}"
        else
            FMT="str"
            # fastSTRUCTURE requires the input without the .str extension;
            # the file itself must be named <stem>.str on disk.
            # If the file is not already named .str we create a symlink.
            if echo "{input.infile}" | grep -qv '\.str$'; then
                SYMLINK="{input.infile}.str"
                ln -sf "{input.infile}" "$SYMLINK" 2>/dev/null || true
                INFILE_ARG="{input.infile}"
            else
                INFILE_ARG="{params.infile_stem}"
            fi
        fi

        CMD="{params.bin} \
             -K {wildcards.k} \
             --input $INFILE_ARG \
             --output {params.output_stem} \
             --format $FMT \
             --prior {params.prior} \
             --seed {params.seed}"

        if [ -n "{params.extra}" ]; then
            CMD="$CMD {params.extra}"
        fi

        echo "Running: $CMD" > {log}
        $CMD >> {log} 2>&1
        """
