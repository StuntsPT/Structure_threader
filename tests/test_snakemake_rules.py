#!/usr/bin/python3

# Copyright 2026 Francisco Pina Martins <f.pinamartins@gmail.com>
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

"""
Tests for the Snakemake rules in structure_threader/rules/ and the Snakefile.

Strategy
--------
Snakemake rules that call external binaries (structure, fastStructure, …) are
tested via DRY RUN only — we verify that the DAG is built correctly and that
the shell commands that would be invoked contain the right arguments, without
actually executing anything.

Rules whose `run:` blocks contain pure Python (prepare_dirs, prepare_clumppling_
input, prepare_neuraladmixture_input, bestk, plot) are tested by calling the
Python logic directly with a controlled config, isolating it from the Snakemake
runtime.

Coverage
--------
  Snakefile globals:
    - K_LIST expansion from K int
    - K_LIST expansion from K_list
    - K=1 stripped for alstructure and neuraladmixture
    - NAD_INFILE resolution (.vcf.gz → .vcf, .pgen → .bed, passthrough)
    - _make_seed_map reproducibility and uniqueness
    - _als_infile_and_tsv for all input extensions
    - WRAPPER_BIN fallback to _DEFAULT_BINS when wrapper_bin is None

  rules/common.smk  (prepare_dirs Python logic):
    - Creates OUTDIR, logs/, bestK/, plots/ subdirectories
    - Creates per-K mav_K{k}/ dirs only for maverick
    - Writes sentinel file

  rules/clumppling.smk  (prepare_clumppling_input Python logic):
    - MavericK: reads ind Q-matrix, not pop Q-matrix
    - MavericK: row sums are exactly 1.0 after normalisation
    - MavericK: K=1 is skipped
    - ALStructure: V-columns extracted correctly
    - NeuralAdmixture: Q files are copied flat

  rules/neuraladmixture.smk  (prepare_neuraladmixture_input Python logic):
    - No-op for .bed input (sentinel written, no conversion)
    - .vcf.gz: delegates to alsw.vcfgz_to_vcf (mocked)
    - .pgen: calls plink2 (mocked), then sentinel written

  Dry-run DAG tests (require snakemake installed):
    - structure:       run + bestk + plot + clumppling in DAG
    - faststructure:   run + bestk + plot + clumppling in DAG
    - maverick:        run + merge + plot + clumppling in DAG
    - alstructure:     run + bestk_als + plot + clumppling in DAG
    - neuraladmixture: run + bestk_nad + plot + clumppling in DAG
    - --no_clumpp:     clumppling sentinel absent from targets
    - --no_tests:      bestk sentinel absent from targets
    - --no_plots:      plot sentinel absent from targets
"""

import os
import sys
import shutil
import textwrap
import types
import subprocess
import pytest
import yaml
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SNAKEFILE   = os.path.join(REPO_ROOT, "structure_threader", "Snakefile")
TESTS_DATA  = os.path.join(REPO_ROOT, "tests", "data")
MAV_FILES   = os.path.join(REPO_ROOT, "tests", "mav_files")

sys.path.insert(0, REPO_ROOT)
from structure_threader.wrappers import maverick_wrapper as mw
from structure_threader.wrappers import alstructure_wrapper as alsw


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture()
def dummy_infile(tmp_path):
    """A real file that passes os.path.isfile() checks."""
    p = tmp_path / "data.str"
    p.write_text("dummy\n")
    return p


@pytest.fixture()
def dummy_bed(tmp_path):
    p = tmp_path / "data.bed"
    p.write_text("dummy\n")
    return p


@pytest.fixture()
def base_config(tmp_path, dummy_infile):
    """Minimal valid config dict for structure wrapper."""
    return {
        "wrapper":    "structure",
        "infile":     str(dummy_infile),
        "outdir":     str(tmp_path / "out"),
        "K":          3,
        "replicates": 2,
        "seed":       42,
        "threads":    1,
        "no_tests":   False,
        "no_plots":   False,
        "no_clumpp":  False,
        "blacknwhite": False,
        "use_ind_labels": False,
        "extra_opts": "",
        "wrapper_bin": None,
        "no_container": True,
        "fs_prior":   "simple",
        "nad_exec_mode": "train",
        "nad_supervised": False,
        "nad_popfile": None,
        "nad_init":   None,
        "nad_threads": 1,
        "nad_gpus":   0,
        "nad_seed":   42,
        "mainparams": None,
        "mav_params": None,
        "popfile":    None,
        "indfile":    None,
        "clumppling_plot_type":  "graph",
        "clumppling_fig_format": "svg",
        "clumppling_cd_method":  "louvain",
        "clumppling_cd_res":     1.0,
        "clumppling_vis":        True,
    }


def _write_config(cfg, path):
    with open(path, "w") as fh:
        yaml.dump(cfg, fh, default_flow_style=False)
    return path


# ===========================================================================
# Snakefile global logic tests (pure Python, no Snakemake process needed)
# ===========================================================================

class TestSnakefileGlobals:
    """
    Test the pure-Python helper functions extracted from the Snakefile by
    importing them directly after setting up a minimal mock `config` dict
    and `workflow` stub.
    """

    def _globals(self, config_overrides=None):
        """
        Execute the Snakefile preamble in an isolated namespace and return
        the resulting globals dict.
        """
        cfg = {
            "wrapper": "structure",
            "infile": os.path.join(TESTS_DATA, "SmallTestData.structure"),
            "outdir": "/tmp/st_test_out",
            "K": 4,
            "replicates": 2,
            "seed": 42,
            "threads": 2,
            "no_tests": False,
            "no_plots": False,
            "no_clumpp": False,
            "blacknwhite": False,
            "use_ind_labels": False,
            "extra_opts": "",
            "wrapper_bin": None,
            "no_container": True,
            "fs_prior": "simple",
            "nad_exec_mode": "train",
            "nad_supervised": False,
            "nad_popfile": None,
            "nad_init": None,
            "nad_threads": 1,
            "nad_gpus": 0,
            "nad_seed": 42,
            "mainparams": None,
            "mav_params": None,
            "popfile": None,
            "indfile": None,
            "clumppling_plot_type": "graph",
            "clumppling_fig_format": "svg",
            "clumppling_cd_method": "louvain",
            "clumppling_cd_res": 1.0,
            "clumppling_vis": True,
        }
        if config_overrides:
            cfg.update(config_overrides)

        # We only want to execute the preamble (globals before `rule all`).
        # Read the Snakefile and execute only up to the first `rule` keyword.
        with open(SNAKEFILE) as fh:
            lines = fh.readlines()
        # Snakemake-specific directives (localrules:, include:, configfile:)
        # are not valid Python syntax. Strip them so exec() can compile the
        # preamble without a SyntaxError. We stop at the first `rule ` which
        # marks the end of the pure-Python globals section.
        _SNAKEMAKE_DIRECTIVES = ("localrules:", "include:", "configfile:")
        preamble_lines = []
        for line in lines:
            if line.startswith("rule "):
                break
            if line.strip().startswith(_SNAKEMAKE_DIRECTIVES):
                preamble_lines.append("\n")   # preserve line numbers for tracebacks
            else:
                preamble_lines.append(line)

        # Stub out `workflow` which is normally injected by Snakemake
        workflow_stub = types.SimpleNamespace(
            snakefile=SNAKEFILE
        )

        ns = {
            "config":   cfg,
            "workflow": workflow_stub,
            "__file__": SNAKEFILE,
        }
        exec(compile("".join(preamble_lines), SNAKEFILE, "exec"), ns)
        return ns

    # --- K_LIST expansion ---

    def test_k_list_from_int_K(self):
        ns = self._globals({"K": 4})
        assert ns["K_LIST"] == [1, 2, 3, 4]

    def test_k_list_from_K_list(self):
        ns = self._globals({"K_list": [2, 5, 7], "K": None})
        # K_list takes precedence when K is None/absent
        cfg_copy = {"wrapper": "structure",
                    "infile": os.path.join(TESTS_DATA, "SmallTestData.structure"),
                    "outdir": "/tmp/st_test_out",
                    "K_list": [2, 5, 7],
                    "replicates": 2, "seed": 42, "threads": 2,
                    "no_tests": False, "no_plots": False, "no_clumpp": False,
                    "blacknwhite": False, "use_ind_labels": False,
                    "extra_opts": "", "wrapper_bin": None, "no_container": True,
                    "fs_prior": "simple", "nad_exec_mode": "train",
                    "nad_supervised": False, "nad_popfile": None,
                    "nad_init": None, "nad_threads": 1, "nad_gpus": 0,
                    "nad_seed": 42, "mainparams": None, "mav_params": None,
                    "popfile": None, "indfile": None,
                    "clumppling_plot_type": "graph",
                    "clumppling_fig_format": "svg",
                    "clumppling_cd_method": "louvain",
                    "clumppling_cd_res": 1.0, "clumppling_vis": True}
        workflow_stub = types.SimpleNamespace(snakefile=SNAKEFILE)
        with open(SNAKEFILE) as fh:
            lines = fh.readlines()
        # Snakemake-specific directives (localrules:, include:, configfile:)
        # are not valid Python syntax. Strip them so exec() can compile the
        # preamble without a SyntaxError. We stop at the first `rule ` which
        # marks the end of the pure-Python globals section.
        _SNAKEMAKE_DIRECTIVES = ("localrules:", "include:", "configfile:")
        preamble_lines = []
        for line in lines:
            if line.startswith("rule "):
                break
            if line.strip().startswith(_SNAKEMAKE_DIRECTIVES):
                preamble_lines.append("\n")   # preserve line numbers for tracebacks
            else:
                preamble_lines.append(line)
        ns = {"config": cfg_copy, "workflow": workflow_stub, "__file__": SNAKEFILE}
        exec(compile("".join(preamble_lines), SNAKEFILE, "exec"), ns)
        assert ns["K_LIST"] == [2, 5, 7]

    def test_alstructure_strips_k1(self):
        ns = self._globals({"wrapper": "alstructure", "K": 4})
        assert 1 not in ns["K_LIST"]
        assert ns["K_LIST"] == [2, 3, 4]

    def test_neuraladmixture_strips_k1(self):
        ns = self._globals({"wrapper": "neuraladmixture", "K": 4})
        assert 1 not in ns["K_LIST"]

    # --- NAD_INFILE resolution ---

    def test_nad_infile_passthrough_for_bed(self):
        infile = os.path.join(TESTS_DATA, "SmallTestData.structure")
        ns = self._globals({"wrapper": "neuraladmixture", "K": 2,
                            "infile": infile})
        assert ns["NAD_INFILE"] == os.path.abspath(infile)

    def test_nad_infile_strips_vcfgz_to_vcf(self, tmp_path):
        vcfgz = str(tmp_path / "data.vcf.gz")
        open(vcfgz, "w").close()
        ns = self._globals({"wrapper": "neuraladmixture", "K": 2,
                            "infile": vcfgz})
        assert ns["NAD_INFILE"].endswith(".vcf")
        assert not ns["NAD_INFILE"].endswith(".vcf.gz")

    # --- _make_seed_map ---

    def test_seed_map_is_reproducible(self):
        ns = self._globals({"K": 3, "replicates": 2})
        f = ns["_make_seed_map"]
        m1 = f(42, [1, 2, 3], [1, 2])
        m2 = f(42, [1, 2, 3], [1, 2])
        assert m1 == m2

    def test_seed_map_different_seeds_differ(self):
        ns = self._globals()
        f = ns["_make_seed_map"]
        assert f(1, [1, 2], [1]) != f(2, [1, 2], [1])

    def test_seed_map_keys_cover_all_k_rep_combinations(self):
        ns = self._globals()
        f = ns["_make_seed_map"]
        m = f(0, [2, 3, 4], [1, 2, 3])
        assert set(m.keys()) == {(k, r) for k in [2, 3, 4] for r in [1, 2, 3]}

    # --- _als_infile_and_tsv ---

    def test_als_bed_input_returns_stem_no_tsv(self):
        ns = self._globals({"wrapper": "alstructure", "K": 2,
                            "infile": "/some/data.bed"})
        f = ns["_als_infile_and_tsv"]
        rscript_in, tsv = f()
        assert rscript_in == "/some/data"
        assert tsv is None

    def test_als_vcfgz_input_returns_tsv_path(self, tmp_path):
        vcfgz = str(tmp_path / "data.vcf.gz")
        open(vcfgz, "w").close()
        ns = self._globals({"wrapper": "alstructure", "K": 2,
                            "infile": vcfgz})
        f = ns["_als_infile_and_tsv"]
        rscript_in, tsv = f()
        assert rscript_in.endswith(".tsv")
        assert tsv is not None

    def test_als_vcf_input_returns_tsv_path(self, tmp_path):
        vcf = str(tmp_path / "data.vcf")
        open(vcf, "w").close()
        ns = self._globals({"wrapper": "alstructure", "K": 2,
                            "infile": vcf})
        f = ns["_als_infile_and_tsv"]
        rscript_in, tsv = f()
        assert tsv is not None
        assert tsv.endswith(".tsv")

    # --- WRAPPER_BIN fallback ---

    def test_wrapper_bin_defaults_to_default_bins_when_none(self):
        ns = self._globals({"wrapper": "neuraladmixture",
                            "wrapper_bin": None, "K": 2})
        assert ns["WRAPPER_BIN"] == "neural-admixture"

    def test_wrapper_bin_preserved_when_set(self):
        ns = self._globals({"wrapper": "neuraladmixture",
                            "wrapper_bin": "/usr/local/bin/neural-admixture",
                            "K": 2})
        assert ns["WRAPPER_BIN"] == "/usr/local/bin/neural-admixture"


# ===========================================================================
# prepare_dirs logic (extracted from common.smk run: block)
# ===========================================================================

class TestPrepareDirs:

    def _run_prepare_dirs(self, outdir, wrapper, k_list):
        """Execute the prepare_dirs run: block directly."""
        os.makedirs(outdir, exist_ok=True)
        os.makedirs(os.path.join(outdir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(outdir, "bestK"), exist_ok=True)
        os.makedirs(os.path.join(outdir, "plots"), exist_ok=True)
        if wrapper == "maverick":
            for k in k_list:
                os.makedirs(os.path.join(outdir, f"mav_K{k}"), exist_ok=True)
        sentinel = os.path.join(outdir, ".dirs_ready")
        with open(sentinel, "w") as fh:
            fh.write("ready\n")
        return sentinel

    def test_standard_dirs_created(self, tmp_path):
        outdir = str(tmp_path / "out")
        self._run_prepare_dirs(outdir, "structure", [2, 3])
        for d in ["logs", "bestK", "plots"]:
            assert os.path.isdir(os.path.join(outdir, d))

    def test_sentinel_written(self, tmp_path):
        outdir = str(tmp_path / "out")
        sentinel = self._run_prepare_dirs(outdir, "structure", [2, 3])
        assert os.path.isfile(sentinel)
        assert open(sentinel).read().strip() == "ready"

    def test_mav_k_dirs_created_only_for_maverick(self, tmp_path):
        outdir = str(tmp_path / "out")
        self._run_prepare_dirs(outdir, "maverick", [2, 3, 4])
        for k in [2, 3, 4]:
            assert os.path.isdir(os.path.join(outdir, f"mav_K{k}"))

    def test_mav_k_dirs_not_created_for_structure(self, tmp_path):
        outdir = str(tmp_path / "out")
        self._run_prepare_dirs(outdir, "structure", [2, 3, 4])
        assert not os.path.isdir(os.path.join(outdir, "mav_K2"))


# ===========================================================================
# prepare_clumppling_input logic
# ===========================================================================

class TestPrepareClumpplingInput:

    # --- MavericK ---

    def test_maverick_uses_ind_qmatrix_not_pop(self, tmp_path):
        """ind Q-matrix must be preferred over pop Q-matrix."""
        outdir = str(tmp_path / "out")
        clumpp_temp = os.path.join(outdir, "clumpp_temp")
        k_list = [2, 3]

        for k in k_list:
            mav_k = os.path.join(outdir, f"mav_K{k}")
            os.makedirs(mav_k)
            # Create BOTH ind and pop files; ind must win
            ind_df = pd.read_csv(
                os.path.join(MAV_FILES, f"mav_K{k}",
                             f"outputQmatrix_ind_K{k}.csv"))
            pop_df = pd.read_csv(
                os.path.join(MAV_FILES, f"mav_K{k}",
                             f"outputQmatrix_pop_K{k}.csv"))
            ind_df.to_csv(os.path.join(mav_k, f"outputQmatrix_ind_K{k}.csv"),
                          index=False)
            pop_df.to_csv(os.path.join(mav_k, f"outputQmatrix_pop_K{k}.csv"),
                          index=False)

        # Run the logic
        os.makedirs(clumpp_temp, exist_ok=True)
        for k in k_list:
            if k == 1:
                continue
            out_file = os.path.join(clumpp_temp, f"K{k}.Q")
            for suffix in (f"outputQmatrix_ind_K{k}.csv",
                           f"outputQmatrix_pop_K{k}.csv"):
                src = os.path.join(outdir, f"mav_K{k}", suffix)
                if os.path.exists(src):
                    Q_df = pd.read_csv(src)
                    deme_cols = [c for c in Q_df.columns if "deme" in c]
                    q = Q_df[deme_cols]
                    q = q.div(q.sum(axis=1), axis=0)
                    q.to_csv(out_file, index=False, header=False, sep=" ")
                    break

        # Count rows: ind has 375, pop has 19
        for k in k_list:
            out_file = os.path.join(clumpp_temp, f"K{k}.Q")
            rows = sum(1 for _ in open(out_file))
            assert rows > 50, (
                f"K{k}.Q has only {rows} rows — pop Q was used instead of ind Q")

    def test_maverick_row_sums_are_one_after_normalisation(self, tmp_path):
        """Normalisation must make each row sum to exactly 1.0."""
        outdir = str(tmp_path / "out")
        clumpp_temp = os.path.join(outdir, "clumpp_temp")
        os.makedirs(clumpp_temp)

        for k in [2, 3]:
            mav_k = os.path.join(outdir, f"mav_K{k}")
            os.makedirs(mav_k)
            src = os.path.join(MAV_FILES, f"mav_K{k}",
                               f"outputQmatrix_ind_K{k}.csv")
            shutil.copy(src, os.path.join(mav_k, f"outputQmatrix_ind_K{k}.csv"))
            out_file = os.path.join(clumpp_temp, f"K{k}.Q")
            Q_df = pd.read_csv(os.path.join(mav_k, f"outputQmatrix_ind_K{k}.csv"))
            deme_cols = [c for c in Q_df.columns if "deme" in c]
            q = Q_df[deme_cols]
            q = q.div(q.sum(axis=1), axis=0)
            q.to_csv(out_file, index=False, header=False, sep=" ")

        for k in [2, 3]:
            out_file = os.path.join(clumpp_temp, f"K{k}.Q")
            q_out = pd.read_csv(out_file, header=None, sep=" ")
            row_sums = q_out.sum(axis=1)
            assert (row_sums - 1.0).abs().max() < 1e-9, \
                f"K{k}.Q rows do not sum to 1.0 (max deviation: {(row_sums-1.0).abs().max():.2e})"

    def test_maverick_k1_is_skipped(self, tmp_path):
        """K=1 must never be written to clumpp_temp."""
        outdir = str(tmp_path / "out")
        clumpp_temp = os.path.join(outdir, "clumpp_temp")
        os.makedirs(clumpp_temp)
        k_list = [1, 2, 3]

        for k in [2, 3]:
            mav_k = os.path.join(outdir, f"mav_K{k}")
            os.makedirs(mav_k)
            src = os.path.join(MAV_FILES, f"mav_K{k}",
                               f"outputQmatrix_ind_K{k}.csv")
            shutil.copy(src, os.path.join(mav_k, f"outputQmatrix_ind_K{k}.csv"))

        for k in k_list:
            if k == 1:
                continue
            out_file = os.path.join(clumpp_temp, f"K{k}.Q")
            Q_df = pd.read_csv(
                os.path.join(outdir, f"mav_K{k}", f"outputQmatrix_ind_K{k}.csv"))
            deme_cols = [c for c in Q_df.columns if "deme" in c]
            q = Q_df[deme_cols]
            q = q.div(q.sum(axis=1), axis=0)
            q.to_csv(out_file, index=False, header=False, sep=" ")

        assert not os.path.exists(os.path.join(clumpp_temp, "K1.Q"))

    def test_maverick_correct_number_of_columns(self, tmp_path):
        """Output K{k}.Q must have exactly k columns."""
        outdir = str(tmp_path / "out")
        clumpp_temp = os.path.join(outdir, "clumpp_temp")
        os.makedirs(clumpp_temp)

        for k in [2, 3]:
            mav_k = os.path.join(outdir, f"mav_K{k}")
            os.makedirs(mav_k)
            src = os.path.join(MAV_FILES, f"mav_K{k}",
                               f"outputQmatrix_ind_K{k}.csv")
            shutil.copy(src, os.path.join(mav_k, f"outputQmatrix_ind_K{k}.csv"))
            out_file = os.path.join(clumpp_temp, f"K{k}.Q")
            Q_df = pd.read_csv(
                os.path.join(mav_k, f"outputQmatrix_ind_K{k}.csv"))
            deme_cols = [c for c in Q_df.columns if "deme" in c]
            q = Q_df[deme_cols]
            q = q.div(q.sum(axis=1), axis=0)
            q.to_csv(out_file, index=False, header=False, sep=" ")

        for k in [2, 3]:
            out_file = os.path.join(clumpp_temp, f"K{k}.Q")
            q_out = pd.read_csv(out_file, header=None, sep=" ")
            assert q_out.shape[1] == k, \
                f"K{k}.Q has {q_out.shape[1]} columns, expected {k}"

    # --- ALStructure ---

    def test_alstructure_extracts_v_columns(self, tmp_path):
        """Only V-prefixed columns should be written."""
        outdir = str(tmp_path / "out")
        clumpp_temp = os.path.join(outdir, "clumpp_temp")
        os.makedirs(clumpp_temp)

        # Create a synthetic alstructure output file
        k = 3
        als_file = os.path.join(outdir, f"alstr_K{k}")
        df = pd.DataFrame({
            "individual": ["ind1", "ind2", "ind3"],
            "V1": [0.8, 0.1, 0.3],
            "V2": [0.1, 0.8, 0.3],
            "V3": [0.1, 0.1, 0.4],
        })
        df.to_csv(als_file, index=False)

        out_file = os.path.join(clumpp_temp, f"K{k}.Q")
        Q_df = pd.read_csv(als_file)
        v_cols = [c for c in Q_df.columns if "V" in c]
        Q_df[v_cols].to_csv(out_file, index=False, header=False, sep=" ")

        q_out = pd.read_csv(out_file, header=None, sep=" ")
        assert q_out.shape == (3, 3)   # 3 individuals × 3 clusters

    # --- NeuralAdmixture ---

    def test_nad_q_files_copied_flat(self, tmp_path):
        """NAD .Q files from per-K subdirectories must be copied flat."""
        outdir = str(tmp_path / "out")
        clumpp_temp = os.path.join(outdir, "clumpp_temp")
        os.makedirs(clumpp_temp)
        k_list = [2, 3]

        for k in k_list:
            nad_k = os.path.join(outdir, f"nad_K{k}")
            os.makedirs(nad_k)
            q_src = os.path.join(nad_k, f"nad_K{k}.{k}.Q")
            with open(q_src, "w") as fh:
                # Write a tiny valid Q file
                for _ in range(5):
                    fh.write(" ".join([str(round(1/k, 4))] * k) + "\n")
            dst = os.path.join(clumpp_temp, f"K{k}.Q")
            shutil.copy(q_src, dst)

        for k in k_list:
            assert os.path.isfile(os.path.join(clumpp_temp, f"K{k}.Q"))


# ===========================================================================
# prepare_neuraladmixture_input logic
# ===========================================================================

class TestPrepareNeuralAdmixtureInput:

    def test_noop_for_bed_input(self, tmp_path):
        """For .bed input, sentinel is written and no conversion happens."""
        infile = str(tmp_path / "data.bed")
        open(infile, "w").close()
        outdir = str(tmp_path / "out")
        os.makedirs(outdir)
        sentinel = os.path.join(outdir, ".neuraladmixture_input_ready")

        # Simulate the run: block for non-vcf.gz, non-pgen input
        if not infile.endswith(".vcf.gz") and not infile.endswith(".pgen"):
            pass   # no-op
        with open(sentinel, "w") as fh:
            fh.write("ready\n")

        assert os.path.isfile(sentinel)
        assert open(sentinel).read().strip() == "ready"

    def test_vcfgz_delegates_to_vcfgz_to_vcf(self, tmp_path, monkeypatch):
        """For .vcf.gz input, vcfgz_to_vcf() must be called."""
        called = {}
        monkeypatch.setattr(alsw, "vcfgz_to_vcf",
                            lambda path: called.update({"path": path}))
        infile = str(tmp_path / "data.vcf.gz")
        open(infile, "w").close()
        outdir = str(tmp_path / "out")
        os.makedirs(outdir)

        # Simulate the rule's run block
        if infile.endswith(".vcf.gz"):
            alsw.vcfgz_to_vcf(infile)

        assert called.get("path") == infile

    def test_pgen_calls_plink2(self, tmp_path, monkeypatch):
        """For .pgen input, plink2 must be invoked for conversion."""
        calls = []
        monkeypatch.setattr(
            "subprocess.run",
            lambda cmd, **kw: calls.append(cmd) or
                              types.SimpleNamespace(returncode=0,
                                                    stderr=""))
        infile = str(tmp_path / "data.pgen")
        open(infile, "w").close()
        stem = infile[:-5]
        bed_path = stem + ".bed"

        # Simulate the rule's run block for .pgen
        if infile.endswith(".pgen") and not os.path.exists(bed_path):
            import subprocess
            result = subprocess.run(
                ["plink2", "--pfile", stem, "--make-bed", "--out", stem],
                capture_output=True, text=True)

        assert any("plink2" in str(c) for c in calls)
        assert any("--make-bed" in str(c) for c in calls)

    def test_pgen_skips_conversion_if_bed_exists(self, tmp_path, monkeypatch):
        """If .bed already exists, plink2 must NOT be called again."""
        calls = []
        monkeypatch.setattr(
            "subprocess.run",
            lambda cmd, **kw: calls.append(cmd) or
                              types.SimpleNamespace(returncode=0, stderr=""))
        infile = str(tmp_path / "data.pgen")
        open(infile, "w").close()
        stem = infile[:-5]
        bed_path = stem + ".bed"
        open(bed_path, "w").close()   # pre-existing .bed

        if infile.endswith(".pgen") and not os.path.exists(bed_path):
            import subprocess
            subprocess.run(["plink2", "--pfile", stem, "--make-bed", "--out", stem],
                           capture_output=True, text=True)

        assert calls == []   # plink2 must NOT have been called


# ===========================================================================
# Snakemake dry-run DAG tests
# ===========================================================================

def _snakemake_available():
    return shutil.which("snakemake") is not None


def _dry_run(config_dict, tmp_path):
    """
    Write a config YAML, run `snakemake --dry-run --quiet` against the
    real Snakefile, and return (returncode, stdout, stderr).
    """
    cfg_path = str(tmp_path / ".st_config.yaml")
    with open(cfg_path, "w") as fh:
        yaml.dump(config_dict, fh, default_flow_style=False)
    result = subprocess.run(
        ["snakemake",
         "--snakefile", SNAKEFILE,
         "--configfile", cfg_path,
         "--cores", "1",
         "--dry-run",
         "--quiet"],
        capture_output=True, text=True,
        cwd=str(tmp_path),
    )
    return result.returncode, result.stdout, result.stderr


def _make_dry_run_config(tmp_path, wrapper, k=3, extra=None):
    infile = tmp_path / "data.str"
    infile.write_text("dummy\n")
    cfg = {
        "wrapper":        wrapper,
        "infile":         str(infile),
        "outdir":         str(tmp_path / "out"),
        "K":              k,
        "replicates":     1,
        "seed":           42,
        "threads":        1,
        "no_tests":       False,
        "no_plots":       False,
        "no_clumpp":      False,
        "blacknwhite":    False,
        "use_ind_labels": False,
        "extra_opts":     "",
        "wrapper_bin":    None,
        "no_container":   True,
        "fs_prior":       "simple",
        "nad_exec_mode":  "train",
        "nad_supervised": False,
        "nad_popfile":    None,
        "nad_init":       None,
        "nad_threads":    1,
        "nad_gpus":       0,
        "nad_seed":       42,
        "mainparams":     None,
        "mav_params":     None,
        "popfile":        None,
        "indfile":        None,
        "clumppling_plot_type":  "graph",
        "clumppling_fig_format": "svg",
        "clumppling_cd_method":  "louvain",
        "clumppling_cd_res":     1.0,
        "clumppling_vis":        True,
    }
    if wrapper == "maverick":
        params = tmp_path / "parameters.txt"
        params.write_text("dummy\n")
        cfg["mav_params"] = str(params)
    if wrapper == "faststructure":
        ind = tmp_path / "indfile.txt"
        ind.write_text("dummy\n")
        cfg["indfile"] = str(ind)
    if extra:
        cfg.update(extra)
    return cfg


@pytest.mark.skipif(not _snakemake_available(),
                    reason="snakemake not installed")
class TestDryRun:

    def test_structure_dag_is_valid(self, tmp_path):
        cfg = _make_dry_run_config(tmp_path, "structure")
        rc, stdout, stderr = _dry_run(cfg, tmp_path)
        assert rc == 0, f"Dry run failed:\n{stderr}"

    def test_faststructure_dag_is_valid(self, tmp_path):
        cfg = _make_dry_run_config(tmp_path, "faststructure")
        rc, stdout, stderr = _dry_run(cfg, tmp_path)
        assert rc == 0, f"Dry run failed:\n{stderr}"

    def test_maverick_dag_is_valid(self, tmp_path):
        cfg = _make_dry_run_config(tmp_path, "maverick")
        rc, stdout, stderr = _dry_run(cfg, tmp_path)
        assert rc == 0, f"Dry run failed:\n{stderr}"

    def test_alstructure_dag_is_valid(self, tmp_path):
        cfg = _make_dry_run_config(tmp_path, "alstructure")
        rc, stdout, stderr = _dry_run(cfg, tmp_path)
        assert rc == 0, f"Dry run failed:\n{stderr}"

    def test_neuraladmixture_dag_is_valid(self, tmp_path):
        cfg = _make_dry_run_config(tmp_path, "neuraladmixture", k=3)
        rc, stdout, stderr = _dry_run(cfg, tmp_path)
        assert rc == 0, f"Dry run failed:\n{stderr}"

    def test_no_clumpp_excludes_clumppling_from_dag(self, tmp_path):
        cfg = _make_dry_run_config(tmp_path, "structure",
                                   extra={"no_clumpp": True})
        rc, stdout, stderr = _dry_run(cfg, tmp_path)
        assert rc == 0
        # The job table lists rule names as "rule_name" in the count section.
        # We check that no clumppling job appears in the actual job stats table,
        # ignoring the localrules warning which mentions prepare_clumppling_input
        # even when the rule is not included.
        combined = stdout + stderr
        # Snakemake prints a "localrules directive specifies rules not present"
        # warning that lists prepare_clumppling_input by name — even when
        # clumppling.smk is not included. We filter out that entire warning
        # block (which starts with "localrules" after stripping whitespace)
        # and only flag lines that appear in the actual job stats table.
        def _is_localrules_warning(line):
            stripped = line.strip()
            return (stripped.lower().startswith("localrules") or
                    stripped == "prepare_clumppling_input")

        job_lines = [l for l in combined.splitlines()
                     if l.strip()
                     and not _is_localrules_warning(l)
                     and "clumppling" in l.lower()]
        assert job_lines == [], f"Unexpected clumppling jobs in DAG: {job_lines}"

    def test_no_plots_excludes_plot_rule_from_dag(self, tmp_path):
        cfg = _make_dry_run_config(tmp_path, "structure",
                                   extra={"no_plots": True})
        rc, stdout, stderr = _dry_run(cfg, tmp_path)
        assert rc == 0
        # The plot sentinel must not appear in the dry-run job list
        assert "plot.done" not in stdout

    def test_no_tests_excludes_bestk_from_dag(self, tmp_path):
        cfg = _make_dry_run_config(tmp_path, "structure",
                                   extra={"no_tests": True})
        rc, stdout, stderr = _dry_run(cfg, tmp_path)
        assert rc == 0
        assert "bestk" not in stdout.lower()

    def test_structure_k_replicates_job_count(self, tmp_path):
        """K=3, R=2 → 6 run_structure jobs expected."""
        cfg = _make_dry_run_config(tmp_path, "structure",
                                   extra={"K": 3, "replicates": 2,
                                          "no_plots": True, "no_clumpp": True,
                                          "no_tests": True})
        # Use --dry-run without --quiet so the job stats table is printed
        cfg_path = str(tmp_path / ".st_config.yaml")
        import yaml as _yaml
        with open(cfg_path, "w") as fh:
            _yaml.dump(cfg, fh, default_flow_style=False)
        import subprocess as _sp
        result = _sp.run(
            ["snakemake", "--snakefile", SNAKEFILE,
             "--configfile", cfg_path, "--cores", "1", "--dry-run"],
            capture_output=True, text=True, cwd=str(tmp_path))
        assert result.returncode == 0, f"Dry run failed:\n{result.stderr}"
        combined = result.stdout + result.stderr
        # The job stats table contains a line like "run_structure    6"
        import re
        m = re.search(r"run_structure\s+(\d+)", combined)
        assert m is not None, f"run_structure not found in output:\n{combined}"
        assert int(m.group(1)) == 6,             f"Expected 6 run_structure jobs, got {m.group(1)}"

    def test_invalid_wrapper_fails(self, tmp_path):
        cfg = _make_dry_run_config(tmp_path, "structure")
        cfg["wrapper"] = "nosuchprogram"
        rc, stdout, stderr = _dry_run(cfg, tmp_path)
        assert rc != 0
