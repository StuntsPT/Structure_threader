#!/usr/bin/env python
# encoding: utf-8

# Code taken from http://stackoverflow.com/a/1336640/3091595.
# Thanks to @sorin for providing this coloring method!
#
# Modified to avoid monkey-patching the global logging.StreamHandler.emit,
# which caused crashes when Snakemake (or other libraries) passed None as a
# log message. We now subclass StreamHandler instead of replacing emit on the
# class itself, and guard against non-string messages defensively.

import logging
import platform


class _ColoredStreamHandler(logging.StreamHandler):
    """StreamHandler that prepends ANSI colour codes based on log level."""

    LEVEL_COLORS = {
        logging.CRITICAL: '\x1b[31m',   # red
        logging.ERROR:    '\x1b[31m',   # red
        logging.WARNING:  '\x1b[33m',   # yellow
        logging.INFO:     '\x1b[32m',   # green
        logging.DEBUG:    '\x1b[35m',   # pink
    }
    RESET = '\x1b[0m'

    def emit(self, record):
        # Guard: record.msg may be None (e.g. Snakemake's progress logger)
        if record.msg is not None:
            color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
            record.msg = color + str(record.msg) + self.RESET
        super().emit(record)


def get_colored_logger(name="structure_threader"):
    """
    Return a logger with colour output on non-Windows platforms.
    Use this instead of logging.getLogger() in structure_threader modules
    to avoid affecting third-party loggers (Snakemake, etc.).
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = _ColoredStreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        logger.propagate = False   # don't pass records up to the root logger
    return logger


# ---------------------------------------------------------------------------
# Backward-compatibility shim
# ---------------------------------------------------------------------------
# The original colorer.py patched logging.StreamHandler.emit globally,
# which affected every logger in the process — including Snakemake's.
# We no longer do that. Modules that relied on the global patch will still
# get coloured output if they use the root logger, because we install our
# handler on the root logger below — but only on non-Windows platforms,
# and only with a safe None-guarded emit.

if platform.system() != 'Windows':
    _root_handler = _ColoredStreamHandler()
    _root_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    # Only add if the root logger has no handlers yet (i.e. basicConfig hasn't
    # been called). This avoids duplicating output in well-configured setups.
    _root = logging.getLogger()
    if not _root.handlers:
        _root.addHandler(_root_handler)
