# Output

When *Structure_threader* is invoked, it writes a config file to the output directory and then launches Snakemake. Progress is reported by Snakemake as each job completes, showing the rule name, the K value and replicate being processed, and the path to the log file for that job.

After all jobs are performed, the program will exit with Snakemake's standard completion message.

## Results

After a successful run, inside the directory you selected as the output directory (let's call it "My_results" for the sake of the example), you will find the following:

* In the root of "My_results" you will find the resulting output files for the wrapped program's runs. One file (or directory, in the case of *MavericK* and *Neural ADMIXTURE*) for each replicate of K.
* Under "My_results/bestK" you will find either the results of the "Evanno test", the results of "fastChooseK.py", or the results of the "Thermodynamic Integration" test, depending on what program was wrapped. *ALStructure* and *Neural ADMIXTURE* do not have a bestK method; all tested K values are recorded instead.
* Under "My_results/plots" you will find one plot for each value of K in [SVG format](https://www.w3.org/Graphics/SVG/) and [HTML format](https://www.w3.org/html/).
* Under "My_results/clumpp" you will find the output of the [Clumppling](https://github.com/PopGenClustering/Clumppling) alignment, including alignment graphs and Q-matrix files aligned across K values. This directory is absent if `--no-clumpp` was passed.
* Under "My_results/logs" you will find one log file per rule execution. These are the first place to look if a run fails.
* A hidden file `.structure_threader_config.yaml` is written to the root of "My_results". This contains the full configuration used for the run and can be inspected or edited for reruns.

## Clumppling output

When Clumppling alignment is run (the default), the "My_results/clumpp" directory contains:

* An alignment graph (`all_modes_graph_rep.svg` and related files) showing the relationships between inferred modes across K values, with admixture bar thumbnails for each mode.
* Aligned Q-matrix files for each K, which can be used for downstream analysis or for generating custom plots.
* A summary of the alignment statistics.

Clumppling is particularly useful when multiple replicates are run for each K (e.g. with *Structure*), as it aligns the cluster labelling across replicates before plotting. When only one replicate per K is available (e.g. with *MavericK*, *ALStructure* and *Neural ADMIXTURE*), Clumppling still produces the alignment graph but skips the within-K alignment step.

## Log files

Each rule writes its own log file to "My_results/logs/". If a run fails, the relevant log file will contain the output and error messages from the wrapped program, which is usually sufficient to diagnose the problem.
