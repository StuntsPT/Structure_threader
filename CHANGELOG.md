# *Structure_threader* changelog

## Changes since v1.0.0:

### Bug fixes:
* Fixed issue when best K is 1
* Fixed missing population separators on static .svg plots when using --use-ind-labels
* Fixed key error when providing faststructure format in plot mode

## Changes since v0.4.3:

### New features:
* Allow the program to draw the `.svg` plots only on gray scale (with '-bw' option)
* Allow the program to show individual label names even when population information is provided (with '--show-ind-labels' option)

### Bug fixes:
* Fixed Qvalue sorting when providing an --ind file with two columns