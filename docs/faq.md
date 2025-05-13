# Frequently Asked Questions

## Installing and Using

### I'm using Ubuntu 24.04 and have issues installing *Structure_threader* with `pip` (or `pipx`). Why?

Some dependencies currently rely on a version of Python older than what is included in the latest Ubuntu releases. As such, we recommend using a container, if possible, or a PPA for older Python releases. For more information, check out the [installation page](install.md).

### *Structure_threader* gives me strange errors running the Clumppling analysis!

Clumppling only works with Python versions lower than 3.12 (such as 3.11). As such, for the least problematic experience, we recommend using Python 3.11 for now.

### Neural ADMIXTURE gives me a similar error to Clumppling!

Like Clumppling, Neural ADMIXTURE only works with Python versions lower than 3.12 (such as 3.11). As such, for the least problematic experience, we recommend using Python 3.11 for now.

### Can I use a .vcf.gz file with ALStructure or Neural ADMIXTURE?

As of version 2.0.0, `.vcf.gz` filetype is supported for both ALStructure and Neural ADMIXTURE, with the extracted file being deleted post-run.
