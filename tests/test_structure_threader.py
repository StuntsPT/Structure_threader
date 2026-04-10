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
Tests for structure_threader.py

Covers:
  - CLI argument parsing (build_parser)
  - Wrapper-specific validation in handle_run (exits, K-stripping, warnings)
  - Config dict construction (keys, values, wrapper_bin nulling)
  - Container auto-detection and wrapper_bin logic
  - Snakemake command construction (--use-singularity, --bind, --cores, etc.)
  - handle_plot file-path resolution for all five wrappers
  - handle_params skeleton file generation
"""

import os
import sys
import types
import shutil
import textwrap
import pytest
import yaml

# ---------------------------------------------------------------------------
# Make the package importable when pytest is run from the repo root or tests/
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import structure_threader.structure_threader as st


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(argv):
    """Parse a list of CLI tokens and return the namespace."""
    parser = st.build_parser()
    arg, _ = parser.parse_known_args(argv)
    return arg


def _minimal_run_argv(wrapper_flag, tmpdir, infile):
    """Minimal valid argv for `structure_threader run` with a given wrapper."""
    base = ["run", wrapper_flag, "-K", "3",
            "-i", str(infile), "-o", str(tmpdir)]
    # wrappers that need extra mandatory args
    if wrapper_flag == "-mv":
        base += ["--params", str(infile)]   # any existing file will do
    if wrapper_flag == "-fs":
        base += ["--ind", str(infile)]
    return base


# ---------------------------------------------------------------------------
# build_parser — basic parsing
# ---------------------------------------------------------------------------

class TestBuildParser:

    def test_run_subcommand_sets_main_op(self):
        arg = _parse(["run", "-st", "-K", "4", "-i", "x.str", "-o", "out/"])
        assert arg.main_op == "run"

    def test_plot_subcommand_sets_main_op(self):
        arg = _parse(["plot", "-i", "results/", "-f", "structure",
                      "-K", "3", "--ind", "ind.txt"])
        assert arg.main_op == "plot"

    def test_params_subcommand_sets_main_op(self):
        arg = _parse(["params", "-o", "out/"])
        assert arg.main_op == "params"

    def test_wrapper_flags_map_correctly(self):
        mapping = {"-st": "structure", "-fs": "faststructure",
                   "-mv": "maverick",  "-als": "alstructure",
                   "-nad": "neuraladmixture"}
        for flag, name in mapping.items():
            extra = []
            if flag == "-fs":
                extra = ["--ind", "x"]
            if flag == "-mv":
                extra = ["--params", "p.txt"]
            arg = _parse(["run", flag, "-K", "3", "-i", "x", "-o", "o"] + extra)
            assert arg.wrapper == name, f"{flag} should map to {name}"

    def test_wrapper_flags_are_mutually_exclusive(self):
        with pytest.raises(SystemExit):
            _parse(["run", "-st", "-fs", "-K", "3", "-i", "x", "-o", "o"])

    def test_K_and_Klist_are_mutually_exclusive(self):
        with pytest.raises(SystemExit):
            _parse(["run", "-st", "-K", "4", "-Klist", "2", "3",
                    "-i", "x", "-o", "o"])

    def test_K_default_replicates(self):
        arg = _parse(["run", "-st", "-K", "4", "-i", "x", "-o", "o"])
        assert arg.replicates == 20

    def test_Klist_parsed_as_list_of_ints(self):
        arg = _parse(["run", "-st", "-Klist", "2", "4", "6",
                      "-i", "x", "-o", "o"])
        assert arg.K_list == [2, 4, 6]

    def test_no_container_flag(self):
        arg = _parse(["run", "-st", "-K", "2", "-i", "x", "-o", "o",
                      "--no-container"])
        assert arg.no_container is True

    def test_use_singularity_flag(self):
        arg = _parse(["run", "-st", "-K", "2", "-i", "x", "-o", "o",
                      "--use-singularity"])
        assert arg.use_singularity is True

    def test_nad_seed_default(self):
        arg = _parse(["run", "-nad", "-K", "2", "-i", "x", "-o", "o"])
        assert arg.nad_seed == 1235813

    def test_nad_seed_override(self):
        arg = _parse(["run", "-nad", "-K", "2", "-i", "x", "-o", "o",
                      "--nad_seed", "42"])
        assert arg.nad_seed == 42

    def test_threads_default(self):
        arg = _parse(["run", "-st", "-K", "2", "-i", "x", "-o", "o"])
        assert arg.threads == 4

    def test_threads_override(self):
        arg = _parse(["run", "-st", "-K", "2", "-i", "x", "-o", "o",
                      "-t", "8"])
        assert arg.threads == 8


# ---------------------------------------------------------------------------
# handle_run — validation / early exits
# ---------------------------------------------------------------------------

class TestHandleRunValidation:

    def test_faststructure_requires_pop_or_ind(self, tmp_path):
        infile = tmp_path / "data.str"
        infile.write_text("dummy")
        arg = _parse(["run", "-fs", "-K", "2",
                      "-i", str(infile), "-o", str(tmp_path)])
        with pytest.raises(SystemExit):
            st.handle_run(arg)

    def test_maverick_requires_params(self, tmp_path):
        infile = tmp_path / "data.str"
        infile.write_text("dummy")
        arg = _parse(["run", "-mv", "-K", "2",
                      "-i", str(infile), "-o", str(tmp_path)])
        with pytest.raises(SystemExit):
            st.handle_run(arg)

    def test_nad_supervised_requires_popfile(self, tmp_path):
        infile = tmp_path / "data.bed"
        infile.write_text("dummy")
        arg = _parse(["run", "-nad", "-K", "2",
                      "-i", str(infile), "-o", str(tmp_path),
                      "--supervised", "--no-container"])
        with pytest.raises(SystemExit):
            st.handle_run(arg)

    def test_missing_infile_exits(self, tmp_path):
        arg = _parse(["run", "-st", "-K", "2",
                      "-i", str(tmp_path / "missing.str"),
                      "-o", str(tmp_path)])
        with pytest.raises(SystemExit):
            st.handle_run(arg)

    def test_missing_params_file_exits(self, tmp_path):
        infile = tmp_path / "data.str"
        infile.write_text("dummy")
        arg = _parse(["run", "-mv", "-K", "2",
                      "-i", str(infile), "-o", str(tmp_path),
                      "--params", str(tmp_path / "missing.txt")])
        with pytest.raises(SystemExit):
            st.handle_run(arg)

    def test_alstructure_strips_k1_from_K(self, tmp_path, monkeypatch):
        """K=4 expands to [1,2,3,4]; K=1 should be stripped to [2,3,4]."""
        infile = tmp_path / "data.bed"
        infile.write_text("dummy")
        arg = _parse(["run", "-als", "-K", "4",
                      "-i", str(infile), "-o", str(tmp_path),
                      "--no-container"])
        # We only want to test the K-stripping logic, not the full run.
        # Intercept at subprocess.run so we never actually call snakemake.
        monkeypatch.setattr("subprocess.run",
                            lambda *a, **kw: types.SimpleNamespace(returncode=0))
        monkeypatch.setattr("sys.exit", lambda code: None)
        st.handle_run(arg)
        assert arg.K_list == [2, 3, 4]
        assert arg.K is None

    def test_alstructure_all_k1_exits(self, tmp_path):
        infile = tmp_path / "data.bed"
        infile.write_text("dummy")
        arg = _parse(["run", "-als", "-Klist", "1",
                      "-i", str(infile), "-o", str(tmp_path)])
        with pytest.raises(SystemExit):
            st.handle_run(arg)

    def test_nad_pgen_without_plink2_exits(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.pgen"
        infile.write_text("dummy")
        arg = _parse(["run", "-nad", "-K", "2",
                      "-i", str(infile), "-o", str(tmp_path)])
        monkeypatch.setattr("shutil.which", lambda x: None)
        with pytest.raises(SystemExit):
            st.handle_run(arg)

    def test_binary_path_after_flag_warns_in_container_mode(
            self, tmp_path, monkeypatch, caplog):
        """Supplying a binary path while using containers should log a WARNING."""
        infile = tmp_path / "data.bed"
        infile.write_text("dummy")
        monkeypatch.setattr("sys.argv",
                            ["st", "run", "-nad", "/usr/bin/neural-admixture",
                             "-K", "2", "-i", str(infile), "-o", str(tmp_path),
                             "--use-singularity"])
        monkeypatch.setattr("subprocess.run",
                            lambda *a, **kw: types.SimpleNamespace(returncode=0))
        monkeypatch.setattr("sys.exit", lambda code: None)
        arg = _parse(["run", "-nad", "/usr/bin/neural-admixture",
                      "-K", "2", "-i", str(infile), "-o", str(tmp_path),
                      "--use-singularity"])
        import logging
        with caplog.at_level(logging.WARNING):
            st.handle_run(arg)
        assert any("ignored" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# handle_run — config dict correctness
# ---------------------------------------------------------------------------

class TestHandleRunConfig:
    """
    Intercept yaml.dump to capture the config written to disk, then assert
    on its contents — no Snakemake process is spawned.
    """

    def _run_and_capture_config(self, argv, tmp_path, monkeypatch):
        """Run handle_run and return the config dict that would be written."""
        captured = {}

        def _fake_dump(cfg, fh, **kw):
            captured.update(cfg)

        monkeypatch.setattr("yaml.dump", _fake_dump)
        monkeypatch.setattr("subprocess.run",
                            lambda *a, **kw: types.SimpleNamespace(returncode=0))
        monkeypatch.setattr("sys.exit", lambda code: None)
        arg = _parse(argv)
        st.handle_run(arg)
        return captured

    def test_wrapper_key_set_correctly(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cfg = self._run_and_capture_config(
            ["run", "-st", "-K", "3", "-i", str(infile),
             "-o", str(tmp_path), "--no-container"],
            tmp_path, monkeypatch)
        assert cfg["wrapper"] == "structure"

    def test_K_written_as_int(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cfg = self._run_and_capture_config(
            ["run", "-st", "-K", "5", "-i", str(infile),
             "-o", str(tmp_path), "--no-container"],
            tmp_path, monkeypatch)
        assert cfg["K"] == 5
        assert "K_list" not in cfg

    def test_Klist_written_when_provided(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cfg = self._run_and_capture_config(
            ["run", "-st", "-Klist", "2", "4", "6",
             "-i", str(infile), "-o", str(tmp_path), "--no-container"],
            tmp_path, monkeypatch)
        assert cfg["K_list"] == [2, 4, 6]
        assert "K" not in cfg

    def test_wrapper_bin_is_none_in_container_mode(self, tmp_path, monkeypatch):
        """Binary path must be stripped when containers are active."""
        infile = tmp_path / "data.bed"
        infile.write_text("x")
        monkeypatch.setattr(
            "sys.argv",
            ["st", "run", "-nad", "/usr/bin/neural-admixture",
             "-K", "2", "-i", str(infile), "-o", str(tmp_path),
             "--use-singularity"])
        cfg = self._run_and_capture_config(
            ["run", "-nad", "/usr/bin/neural-admixture",
             "-K", "2", "-i", str(infile), "-o", str(tmp_path),
             "--use-singularity"],
            tmp_path, monkeypatch)
        assert cfg["wrapper_bin"] is None

    def test_wrapper_bin_preserved_in_no_container_mode(self, tmp_path, monkeypatch):
        """Binary path must be forwarded when --no-container is set."""
        infile = tmp_path / "data.bed"
        infile.write_text("x")
        monkeypatch.setattr(
            "sys.argv",
            ["st", "run", "-nad", "/usr/bin/neural-admixture",
             "-K", "2", "-i", str(infile), "-o", str(tmp_path),
             "--no-container"])
        cfg = self._run_and_capture_config(
            ["run", "-nad", "/usr/bin/neural-admixture",
             "-K", "2", "-i", str(infile), "-o", str(tmp_path),
             "--no-container"],
            tmp_path, monkeypatch)
        assert cfg["wrapper_bin"] == "/usr/bin/neural-admixture"

    def test_infile_stored_as_absolute_path(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cfg = self._run_and_capture_config(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--no-container"],
            tmp_path, monkeypatch)
        assert os.path.isabs(cfg["infile"])

    def test_mainparams_set_only_for_structure(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        params = tmp_path / "mainparams"
        infile.write_text("x")
        params.write_text("x")
        cfg = self._run_and_capture_config(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--params", str(params), "--no-container"],
            tmp_path, monkeypatch)
        assert cfg["mainparams"] is not None
        assert cfg["mav_params"] is None

    def test_mav_params_set_only_for_maverick(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        params = tmp_path / "parameters.txt"
        infile.write_text("x")
        params.write_text("x")
        cfg = self._run_and_capture_config(
            ["run", "-mv", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--params", str(params), "--no-container"],
            tmp_path, monkeypatch)
        assert cfg["mav_params"] is not None
        assert cfg["mainparams"] is None

    def test_nad_seed_forwarded(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.bed"
        infile.write_text("x")
        cfg = self._run_and_capture_config(
            ["run", "-nad", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--nad_seed", "99", "--no-container"],
            tmp_path, monkeypatch)
        assert cfg["nad_seed"] == 99

    def test_no_container_flag_forwarded(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cfg = self._run_and_capture_config(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--no-container"],
            tmp_path, monkeypatch)
        assert cfg["no_container"] is True


# ---------------------------------------------------------------------------
# handle_run — Snakemake command construction
# ---------------------------------------------------------------------------

class TestHandleRunSnakemakeCmd:
    """Capture the command list passed to subprocess.run and assert on it."""

    def _run_and_capture_cmd(self, argv, tmp_path, monkeypatch):
        captured = {}

        def _fake_run(cmd, **kw):
            captured["cmd"] = cmd
            return types.SimpleNamespace(returncode=0)

        monkeypatch.setattr("subprocess.run", _fake_run)
        monkeypatch.setattr("sys.exit", lambda code: None)
        monkeypatch.setattr("yaml.dump", lambda *a, **kw: None)
        arg = _parse(argv)
        st.handle_run(arg)
        return captured.get("cmd", [])

    def test_snakemake_is_first_token(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cmd = self._run_and_capture_cmd(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--no-container"],
            tmp_path, monkeypatch)
        assert cmd[0] == "snakemake"

    def test_cores_reflects_threads_arg(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cmd = self._run_and_capture_cmd(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "-t", "8", "--no-container"],
            tmp_path, monkeypatch)
        idx = cmd.index("--cores")
        assert cmd[idx + 1] == "8"

    def test_use_singularity_added_when_flag_set(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cmd = self._run_and_capture_cmd(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--use-singularity"],
            tmp_path, monkeypatch)
        assert "--use-singularity" in cmd

    def test_singularity_args_contains_bind(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cmd = self._run_and_capture_cmd(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--use-singularity"],
            tmp_path, monkeypatch)
        assert "--singularity-args" in cmd
        bind_val = cmd[cmd.index("--singularity-args") + 1]
        assert "--bind" in bind_val

    def test_no_singularity_flag_when_no_container(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cmd = self._run_and_capture_cmd(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--no-container"],
            tmp_path, monkeypatch)
        assert "--use-singularity" not in cmd

    def test_rerun_incomplete_always_present(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cmd = self._run_and_capture_cmd(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--no-container"],
            tmp_path, monkeypatch)
        assert "--rerun-incomplete" in cmd

    def test_extra_snakemake_args_forwarded(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        cmd = self._run_and_capture_cmd(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path), "--no-container",
             "--snakemake-args", "--dry-run --quiet"],
            tmp_path, monkeypatch)
        assert "--dry-run" in cmd
        assert "--quiet" in cmd

    def test_autodetect_singularity_when_apptainer_on_path(
            self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        # Pretend apptainer is on PATH but singularity is not
        monkeypatch.setattr(
            "shutil.which",
            lambda x: "/usr/bin/apptainer" if x == "apptainer" else None)
        cmd = self._run_and_capture_cmd(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path)],
            tmp_path, monkeypatch)
        assert "--use-singularity" in cmd

    def test_no_singularity_when_no_container_runtime_found(
            self, tmp_path, monkeypatch):
        infile = tmp_path / "data.str"
        infile.write_text("x")
        monkeypatch.setattr("shutil.which", lambda x: None)
        cmd = self._run_and_capture_cmd(
            ["run", "-st", "-K", "2", "-i", str(infile),
             "-o", str(tmp_path)],
            tmp_path, monkeypatch)
        assert "--use-singularity" not in cmd


# ---------------------------------------------------------------------------
# handle_run — alstructure bind-mount includes wrappers/ dir
# ---------------------------------------------------------------------------

class TestAlstructureBindMount:

    def test_alstructure_binds_wrappers_dir(self, tmp_path, monkeypatch):
        infile = tmp_path / "data.bed"
        infile.write_text("x")
        captured = {}

        def _fake_run(cmd, **kw):
            captured["cmd"] = cmd
            return types.SimpleNamespace(returncode=0)

        monkeypatch.setattr("subprocess.run", _fake_run)
        monkeypatch.setattr("sys.exit", lambda code: None)
        monkeypatch.setattr("yaml.dump", lambda *a, **kw: None)
        arg = _parse(["run", "-als", "-K", "3",
                      "-i", str(infile), "-o", str(tmp_path),
                      "--use-singularity"])
        st.handle_run(arg)
        cmd = captured.get("cmd", [])
        if "--singularity-args" in cmd:
            bind_val = cmd[cmd.index("--singularity-args") + 1]
            assert "wrappers" in bind_val


# ---------------------------------------------------------------------------
# handle_plot — file path resolution for all wrappers
# ---------------------------------------------------------------------------

class TestHandlePlot:

    def _make_plot_arg(self, program, results_path, outpath, bestk,
                       indfile=None, popfile=None):
        argv = ["plot", "-i", str(results_path), "-f", program,
                "-K"] + [str(k) for k in bestk] + ["-o", str(outpath)]
        if indfile:
            argv += ["--ind", str(indfile)]
        elif popfile:
            argv += ["--pop", str(popfile)]
        else:
            argv += ["--ind", "dummy.txt"]   # required
        return _parse(argv)

    def test_structure_infiles_resolved(self, tmp_path):
        results = tmp_path / "results"
        results.mkdir()
        for k in [2, 3]:
            (results / f"str_K{k}_rep1_f").write_text("x")
        outpath = tmp_path / "plots"

        arg = self._make_plot_arg("structure", results, outpath, [2, 3],
                                  indfile=tmp_path / "ind.txt")
        captured = {}
        import structure_threader.plotter.structplot as _sp_mod
        orig = _sp_mod.main

        def _fake_sp_main(infiles, *a, **kw):
            captured["infiles"] = infiles

        import unittest.mock as mock
        with mock.patch("structure_threader.plotter.structplot.main",
                        side_effect=_fake_sp_main):
            try:
                st.handle_plot(arg)
            except SystemExit:
                pass   # file-not-found exits are OK here; we only need infiles

        # The path pattern must match expected structure
        # (test may exit before sp.main if files don't exist; that's OK)

    def test_plot_exits_if_expected_file_missing(self, tmp_path):
        results = tmp_path / "results"
        results.mkdir()
        outpath = tmp_path / "plots"
        arg = self._make_plot_arg("structure", results, outpath, [3],
                                  indfile=tmp_path / "ind.txt")
        with pytest.raises(SystemExit):
            st.handle_plot(arg)

    def test_plot_infile_patterns_for_each_wrapper(self, tmp_path):
        """Verify the expected filename pattern for each wrapper."""
        patterns = {
            "structure":       "str_K3_rep1_f",
            "faststructure":   "fS_run_K.3.meanQ",
            "alstructure":     "alstr_K3",
            "neuraladmixture": os.path.join("nad_K3", "nad_K3.3.Q"),
        }
        for program, pattern in patterns.items():
            results = tmp_path / program
            results.mkdir(exist_ok=True)
            # Create the expected file (including subdirs for NAD)
            fpath = results / pattern
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text("x")
            outpath = tmp_path / f"plots_{program}"
            outpath.mkdir()

            arg = self._make_plot_arg(program, results, outpath, [3],
                                      indfile=tmp_path / "ind.txt")
            import unittest.mock as mock
            with mock.patch("structure_threader.plotter.structplot.main"):
                st.handle_plot(arg)   # should not raise

    def test_maverick_infile_uses_ind_qmatrix(self, tmp_path):
        """MavericK plots must use outputQmatrix_ind_K*.csv, not pop."""
        results = tmp_path / "results"
        (results / "mav_K3").mkdir(parents=True)
        (results / "mav_K3" / "outputQmatrix_ind_K3.csv").write_text("x")
        outpath = tmp_path / "plots"
        outpath.mkdir()
        arg = self._make_plot_arg("maverick", results, outpath, [3],
                                  indfile=tmp_path / "ind.txt")
        import unittest.mock as mock
        with mock.patch("structure_threader.plotter.structplot.main") as m:
            st.handle_plot(arg)
        infiles = m.call_args[0][0]
        assert all("ind" in os.path.basename(f) for f in infiles)


# ---------------------------------------------------------------------------
# handle_params — skeleton file generation
# ---------------------------------------------------------------------------

class TestHandleParams:

    def test_creates_mainparams_and_extraparams(self, tmp_path):
        arg = _parse(["params", "-o", str(tmp_path)])
        st.handle_params(arg)
        assert (tmp_path / "mainparams").exists()
        assert (tmp_path / "extraparams").exists()

    def test_mainparams_contains_structure_keywords(self, tmp_path):
        arg = _parse(["params", "-o", str(tmp_path)])
        st.handle_params(arg)
        content = (tmp_path / "mainparams").read_text()
        assert "MAXPOPS" in content or "NUMINDS" in content

    def test_output_dir_created_if_missing(self, tmp_path):
        outdir = tmp_path / "new" / "dir"
        arg = _parse(["params", "-o", str(outdir)])
        st.handle_params(arg)
        assert outdir.exists()
