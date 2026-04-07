# rules/structure.smk
# Rule for running STRUCTURE (one job per K × replicate combination).
# Depends on prepare_dirs (via DIRS_SENTINEL) so output directories exist
# before Apptainer tries to bind-mount them.
#
# bestk and plot are in rules/common.smk because their logic is shared
# across wrappers (dispatched on WRAPPER at runtime).


rule run_structure:
    input:
        infile     = INFILE,
        dirs_ready = DIRS_SENTINEL,
        params     = ([MAINPARAMS] if MAINPARAMS else []),
    output:
        # STRUCTURE writes <stem>_f (plus _q, _p, etc.).
        # We declare only _f — the file downstream rules need.
        ffile = os.path.join(OUTDIR, "str_K{k}_rep{rep}_f"),
    params:
        output_stem = lambda wc: os.path.join(OUTDIR,
                                               f"str_K{wc.k}_rep{wc.rep}"),
        seed        = lambda wc: SEED_MAP[(int(wc.k), int(wc.rep))],
        mainparams  = MAINPARAMS or "",
        extra       = config.get("extra_opts", ""),
        bin         = WRAPPER_BIN,
    log:
        os.path.join(OUTDIR, "logs", "structure_K{k}_rep{rep}.log"),
    threads: 1    # STRUCTURE is single-threaded; parallelism = many jobs at once
    container:
        None if NO_CONTAINER else STRUCTURE_IMAGE
    shell:
        """
        CMD="{params.bin} -K {wildcards.k} \
             -i {input.infile} \
             -o {params.output_stem} \
             -D {params.seed}"

        if [ -n "{params.mainparams}" ]; then
            EXTRAPARAMS=$(dirname {params.mainparams})/extraparams
            CMD="$CMD -m {params.mainparams}"
            if [ -f "$EXTRAPARAMS" ]; then
                CMD="$CMD -e $EXTRAPARAMS"
            fi
        fi

        if [ -n "{params.extra}" ]; then
            CMD="$CMD {params.extra}"
        fi

        echo "Running: $CMD" > {log}
        $CMD >> {log} 2>&1
        """
