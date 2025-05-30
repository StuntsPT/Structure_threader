# *Structure_threader* changelog

## Changes since v1.3.11

## New features
* *Structure_threader* now supports Neural ADMIXTURE.
    * *PLINK 2* support is included for Neural ADMIXTURE.
    * Supervised runs are supported, but don't include post-run analysis.
    * More information can be found in the [official Neural ADMIXTURE repo](https://github.com/AI-sandbox/neural-admixture)
* An official Docker image is now available. The Dockerfile can be found in this repo, under helper_scripts.
* Implements a CLUMPP-like analysis using Clumppling.
* Added support for .vcf.gz files (ALStructure and Neural ADMIXTURE).
* The resulting .tsv file for ALStructure is now deleted post-run.
* More information is now shown in each individual step of the run.

## Bug fixes
* Fixes Plotly HTML file not being properly formatted.
* Fixes recent deprecations in setup.py

## Documentation
* Added more information about test data creation.
* Added FAQ due to recent changes.
* Updated install instructions.
* Updated stale links.
* Misc changes.

## Other changes
* Test files have been remade due to changes in the upstream data.
* Restructured the source tree.

---

## Changes since v1.3.10

## Plotting
* Fixes a bug with a corner case of `usepopinfo` when some individuals did not have population attributed (0)

---

## Changes since v1.3.9

## Plotting
* Enables the option to draw ALStructure plots from the `plot` mode.

---

## Changes since v1.3.8

## Documentation
* Clarifies that ALStructure does not currently support Best K estimation.

## Plotting
* Moves the population/individual names on the HTML plot back to the bottom. Somewhere aling the way, plotly must have changed the default to above.

---

## Changes since v1.3.7

## Documentation
* Improves readability and clarifies inline help text for the `plot` option.

---

## Changes since v1.3.6

## Bugfix
* Corrects a bug with `setup.py` not working correctly when installing on Windows platforms.

---

## Changes since v1.3.5

## Bugfix
* Adds a corner case to the STRUCTURE results parser for when the option `#define ANCESTDIST` is set to `1`.

---

## Changes since v1.3.4

## Bugfix
* Improves the shebang on `alstructure_wrapper.R` to improve conda compatibility.

---

## Changes since v1.3.3

## Bugfix
* Forces plotly to version >= 4.1.1 due to a deprecation warning.

---

## Changes since v1.3.2

## Bugfix
* Makes the VCF conversion script handle tri-alellic (and more) SNPs the same way that PLINK does - discard them as NA. I am under the impression that this could be better handled, but for now it will do.

Big thanks to Yamila Paula Cardoso for providing me with a dataset where this bug showed up!

---

## Changes since v1.3.1

## Bugfix
* Fixes a Plotly deprecation warning:

```
/usr/local/lib/python3.6/dist-packages/plotly/tools.py:465: DeprecationWarning:

plotly.tools.make_subplots is deprecated, please use plotly.subplots.make_subplots instead
```

---

## Changes since v1.3.0

## New feature
* *Structure_threader* can now supports passing a VCF file for [ALStructure](https://github.com/StoreyLab/alstructure). Not even upstream *ALStructure* can do this. =-)

---

## Changes since v1.2.15

## New feature
* *Structure_threader* can now wrap [ALStructure](https://github.com/StoreyLab/alstructure)!!! This is a major feature and warranted the release of version 1.3.0.

---

## Changes since v1.2.14

### Bug Fixes
* Fixed a bug that occurred when multiple arguments were passed to `extra_opts` when wrapping *fastStructure*. Thank you to @oviscanadensis for the superb bug report.

---

## Changes since v1.2.13

### Bug Fixes
* Fixed a bug when parsing yet another variant of STRUCTURE output.

---

## Changes since v1.2.12

### Bug Fixes
* Fixed a bug that caused a crash when *MavericK* *alpha* and *alphaPropSD* parameter values were split with both a comma and a white-space. Thank you to Sophie Gresham for reporting it.

---

## Changes since v1.2.11

### New features
* Adds infrastructure to use Gitlab's CI server parallel to Travis CI.

### Bug Fixes
* The field tests coding was improved to drop some hard-coded paths into dynamic ones.

---

## Changes since v1.2.10

### Bug fixes
* Marks `numpy>=1.12.1` dependency. The key issue here being in the version number.

---

## Changes since v1.2.9

### Bug fixes
* Corrects a bug with plotting *MavericK* "Qmatrix" files that did not have a "population identifier" field.

---

## Changes since v1.2.8

### Bug fixes
* Using the `plot` function on *MavericK* results now works as intended.
* Improved and clarified how the `plot` input files should be indicated.

---

## Changes since v1.2.7

### Bug fixes
* *Structure_threader* now always makes a sanity check for `mainparams` and `extraparams`.

### New features:
* New option introduced: `--seed`, which allows the user to define a random seed value. It is not mandatory, and defaults to "1235813".
* *Structure_threader* now checks if the `RANDOMIZE` option is set in the `extraparams` file. If it is, it gets disabled since random seeds are now handled internally.

---

## Changes since v1.2.6

### Bug fixes
* Corrected a bug when sorting plot order using an "indfile" with more than 10 populations.

---

## Changes since v1.2.5

### Bug fixes
* Improved unit and field tests.
* Removed a leftover debugging line.

---

## Changes since v1.2.4

### Bug fixes
* Allows a random seed to be passed to STRUCTURE. This seed will be used to generate *N* seeds, where *N* is the number of runs. Each will be attached to the appropriate CLI.

---

## Changes since v1.2.3

### Bug fixes
* Added an extra sanity check for write permissions to the output directory.

---

## Changes since v1.2.2

### Bug fixes
* The "skeletons" module was not being packaged in Pypi. This is now fixed.

---

## Changes since v1.2.1

### Bug fixes
* Added more underflow protection.

---

## Changes since v1.2.0

### Bug fixes
* Added an underflow protection.
* Added a fail-safe in case of MavericK using a single "MainRepeats" parameter.
* Improved some text strings.

---

## Changes since v1.1.0:

### Bug fixes
* Corrected a few typos in some of the printed messages.
* Fixed a bug with a nonsensical leading "/" on the windows version.
* Corrected a bug where *MavericK* execution stopped due to multiple `alpha` and `alphaPropSD` values being set.
* K plots visualization is now improved when plotting a large number of Ks.

### New features:
* Added option to generate skeleton parameter files (`mainparams` and `extraparams`) for *STRUCTURE*.
* If wrapping *MavericK* with TI option turned off, bestK tests are now skipped.
* Vastly improved unit test suite.
* New presentation of "bestK" evidence when wrapping MavericK.

---

## Changes since v1.0.1:

### Bug fixes:
* Fixed a broken link in the docs (Thanks to @briantrice for finding it).
* Fixed a bug with the file prefixes for drawing plots that required the user to be in the directory where the meanQ files were located.
* Corrected a bug with the way "fastStructure" was spelled
* Corrected a bug with population delimiters.

### New features:
* Sanity checks errors and warnings are now also colored.

---

## Changes since v1.0.0:

### Bug fixes:
* Fixed issue when best K is 1
* Fixed missing population separators on static `.svg` plots when using --use-ind-labels
* Changed a variable name to avoid conflicts, despite being in a different namespace.
* Fixed missing population separators on static .svg plots when using --use-ind-labels
* Fixed key error when providing faststructure format in plot mode

---

## Changes since v0.4.3:

### New features:
* Allow the program to draw the `.svg` plots only on gray scale (with '-bw' option)
* Allow the program to show individual label names even when population information is provided (with '--show-ind-labels' option)

### Bug fixes:
* Fixed Qvalue sorting when providing an --ind file with two columns
