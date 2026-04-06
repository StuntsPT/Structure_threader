# rules/clumppling.smk
# Clumppling alignment — two rules:
#
#   prepare_clumppling_input  (localrule, host-side)
#     Converts MavericK/ALStructure outputs to standard .Q files in a temp
#     directory. No-op for STRUCTURE, fastSTRUCTURE, and NeuralAdmixture,
#     which clumppling can read directly.
#
#   clumppling  (containerised, pure shell:)
#     Calls `python -m clumppling` inside the container.
#     Must be a shell: rule — run: blocks always execute on the host regardless
#     of the container: directive, so clumppling would not be found there.


# ---------------------------------------------------------------------------
# Helper: per-wrapper clumppling settings
# ---------------------------------------------------------------------------

def _clumppling_format():
    return {
        "structure":       "structure",
        "faststructure":   "fastStructure",
        "maverick":        "generalQ",
        "alstructure":     "generalQ",
        "neuraladmixture": "admixture",
    }[WRAPPER]

def _clumppling_extension():
    return {
        "structure":       "_f",
        "faststructure":   ".meanQ",
        "maverick":        ".Q",
        "alstructure":     ".Q",
        "neuraladmixture": ".Q",
    }[WRAPPER]

def _needs_qprep():
    """MavericK, ALStructure, and NeuralAdmixture need files copied to a flat
    temp directory — their .Q files live in per-K subdirectories, but
    clumppling only scans the top level of its input directory."""
    return WRAPPER in ("maverick", "alstructure", "neuraladmixture")

CLUMPPLING_TEMP   = os.path.join(OUTDIR, "clumpp_temp")
CLUMPPLING_OUTDIR = os.path.join(OUTDIR, "clumpp")
CLUMPPLING_INPUT_SENTINEL = os.path.join(OUTDIR, ".clumppling_input_ready")


# ---------------------------------------------------------------------------
# Rule: prepare_clumppling_input  (always localrule — pure Python, host-side)
# For STRUCTURE, fastSTRUCTURE, and NeuralAdmixture this is a no-op that
# just writes the sentinel; the container rule reads directly from OUTDIR.
# For MavericK and ALStructure it extracts Q-matrices into CLUMPPLING_TEMP.
# ---------------------------------------------------------------------------

rule prepare_clumppling_input:
    input:
        files = (all_structure_f_files()      if WRAPPER == "structure"
                 else all_fs_meanq_files()    if WRAPPER == "faststructure"
                 else all_mav_qmatrix_files() if WRAPPER == "maverick"
                 else all_als_qfiles()        if WRAPPER == "alstructure"
                 else all_nad_qfiles()),
    output:
        sentinel = CLUMPPLING_INPUT_SENTINEL,
    run:
        import logging, pandas as pd
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)

        if WRAPPER == "maverick":
            os.makedirs(CLUMPPLING_TEMP, exist_ok=True)
            logging.info("Preparing MavericK Q-matrices for Clumppling …")
            for k in K_LIST:
                out_file = os.path.join(CLUMPPLING_TEMP, f"K{k}.Q")
                for suffix in (f"outputQmatrix_pop_K{k}.csv",
                               f"outputQmatrix_ind_K{k}.csv"):
                    src = os.path.join(OUTDIR, f"mav_K{k}", suffix)
                    if os.path.exists(src):
                        Q_df = pd.read_csv(src)
                        deme_cols = [c for c in Q_df.columns if "deme" in c]
                        Q_df[deme_cols].to_csv(out_file, index=False,
                                               header=False, sep=" ")
                        break

        elif WRAPPER == "alstructure":
            os.makedirs(CLUMPPLING_TEMP, exist_ok=True)
            logging.info("Preparing ALStructure Q-matrices for Clumppling …")
            for k in K_LIST:
                src = os.path.join(OUTDIR, f"alstr_K{k}")
                out_file = os.path.join(CLUMPPLING_TEMP, f"K{k}.Q")
                Q_df = pd.read_csv(src)
                v_cols = [c for c in Q_df.columns if "V" in c]
                Q_df[v_cols].to_csv(out_file, index=False,
                                    header=False, sep=" ")
        elif WRAPPER == "neuraladmixture":
            os.makedirs(CLUMPPLING_TEMP, exist_ok=True)
            logging.info("Copying NeuralAdmixture Q-files to flat temp dir for Clumppling …")
            import shutil
            for k in K_LIST:
                src = os.path.join(OUTDIR, f"nad_K{k}", f"nad_K{k}.{k}.Q")
                dst = os.path.join(CLUMPPLING_TEMP, f"K{k}.Q")
                shutil.copy(src, dst)
        else:
            logging.info(f"{WRAPPER}: no Q-matrix conversion needed.")

        with open(output.sentinel, "w") as fh:
            fh.write("ready\n")


# ---------------------------------------------------------------------------
# Rule: clumppling  (containerised, pure shell:)
# The input directory is either OUTDIR (most wrappers) or CLUMPPLING_TEMP
# (MavericK and ALStructure). Both are already bind-mounted because they are
# subdirectories of OUTDIR which the shim always binds.
# ---------------------------------------------------------------------------

rule clumppling:
    input:
        sentinel = CLUMPPLING_INPUT_SENTINEL,
    output:
        sentinel = os.path.join(OUTDIR, "clumpp", ".clumppling_done"),
    params:
        input_dir  = CLUMPPLING_TEMP if _needs_qprep() else OUTDIR,
        output_dir = CLUMPPLING_OUTDIR,
        fmt        = _clumppling_format(),
        extension  = _clumppling_extension(),
        plot_type  = config.get("clumppling_plot_type", "graph"),
        fig_format = config.get("clumppling_fig_format", "svg"),
        cd_method  = config.get("clumppling_cd_method", "louvain"),
        cd_res     = config.get("clumppling_cd_res", 1.0),
        vis        = config.get("clumppling_vis", True),
        ind_labels = INDFILE or "",
    log:
        os.path.join(OUTDIR, "logs", "clumppling.log"),
    container:
        CLUMPPLING_IMAGE
    shell:
        r"""
        CMD="python -m clumppling \
             -i {params.input_dir} \
             -o {params.output_dir} \
             -f {params.fmt} \
             --extension {params.extension} \
             --plot_type all \
             --fig_format {params.fig_format}"

        if [ -n "{params.ind_labels}" ]; then
            CMD="$CMD --ind_labels {params.ind_labels}"
        fi

        echo "Running: $CMD" > {log}
        $CMD >> {log} 2>&1

        touch {output.sentinel}
        """
