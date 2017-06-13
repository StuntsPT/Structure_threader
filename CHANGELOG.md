# *Structure_threader* changelog

## Changes since v1.1.0:

### Bug fixes
* Corrected a few typos in some of the printed messages
* Fixed a bug with a nonsensical leading "/" on the windows version.

### New features:
* Added option to generate skeleton parameter files (`mainparams` and `extraparams`) for *STRUCTURE*.
* If wrapping *MavericK* with TI option turned off, bestK tests are now skipped.


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
