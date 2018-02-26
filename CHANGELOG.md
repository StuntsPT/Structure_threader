# *Structure_threader* changelog


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
