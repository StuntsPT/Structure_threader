# Frequently Asked Questions

## Installing and Using

### Can I use a `.vcf.gz` file with *ALStructure* or *Neural ADMIXTURE*?

Yes. Both *ALStructure* and *Neural ADMIXTURE* support `.vcf.gz` input. The file is extracted to a temporary `.vcf` on the host before the container job runs, and the extracted file is automatically deleted after the run completes.

### Do I need to install Structure, fastStructure, MavericK, ALStructure or Neural ADMIXTURE myself?

No, as of version 2.1.0. *Structure_threader* runs all wrapped programs inside [Apptainer/Singularity](https://apptainer.org/) containers by default, and pulls the container images automatically. You only need to have Apptainer or Singularity installed on your system. If you prefer to use locally installed binaries, pass `--no-container`.

### I don't have Apptainer or Singularity. Can I still use *Structure_threader*?

Yes. If no container runtime is detected, *Structure_threader* automatically falls back to using locally installed binaries and prints a warning. In this case you will need to have the relevant wrapped program installed and available on your `$PATH`, or provide the path to its binary after the wrapper flag (e.g. `-st /usr/local/bin/structure --no-container`).

### I'm getting an Apptainer error about user namespaces on my HPC cluster or CI system.

This means the system's kernel has unprivileged user namespaces disabled. The solution is to install the SUID version of Apptainer (`apptainer-suid` on Debian/Ubuntu), which does not require user namespaces. If you do not have administrative access to the system, contact your system administrator, or use `--no-container` with locally installed binaries.

### I'm using Ubuntu 24.04 and have issues installing *Structure_threader* with `pip` (or `pipx`). Why?

Some older dependencies may not yet support the latest Python releases. As such, we recommend installing *Structure_threader* via Bioconda with Python 3.11, which is known to work well. For more information, check out the [installation page](install.md).

### Can I use a `.pgen` (PLINK 2) file with *Neural ADMIXTURE*?

Not yet. There is a known bug in *Neural ADMIXTURE* 1.6.7 where reading `.pgen` files fails with a `TypeError`. A fix is pending upstream. In the meantime, please convert your `.pgen` file to `.bed` using `plink2 --pfile <stem> --make-bed --out <stem>` and use the resulting `.bed` file as input.

### *Structure_threader* gives me strange errors running the *Clumppling* alignment!

Make sure Clumppling is installed. When using container mode (the default), Clumppling runs inside its own container automatically. If using `--no-container`, you will need Clumppling installed in the same Python environment as *Structure_threader*.

### How do I re-run just the plotting step without re-running the analysis?

Use the `plot` subcommand:

```
structure_threader plot -i My_results/ -f structure -K 3 4 5 -o My_results/plots/ --ind indfile.txt
```

See the [usage page](usage.md) for the full list of options.
