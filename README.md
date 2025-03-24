# Structure_threader
A program to parallelize the runs of [Structure](https://web.stanford.edu/group/pritchardlab/structure.html),  [fastStructure](https://rajanil.github.io/fastStructure/), [MavericK](https://github.com/bobverity/MavericK), [ALStructure](https://github.com/StoreyLab/alstructure) and [Neural ADMIXTURE](https://github.com/AI-sandbox/neural-admixture) software.

[![Pipeline Status](https://gitlab.com/StuntsPT/Structure_threader/badges/master/pipeline.svg)](https://gitlab.com/StuntsPT/Structure_threader/pipelines)
[![Documentation Status](https://readthedocs.org/projects/structure-threader/badge/?version=latest)](https://structure-threader.readthedocs.io/en/latest/?badge=latest)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/becafd10f0bc4904b6d2857cf4c47ea4)](https://www.codacy.com/gh/StuntsPT/Structure_threader/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=StuntsPT/Structure_threader&amp;utm_campaign=Badge_Grade)
[![DOI](https://zenodo.org/badge/31598374.svg)](https://zenodo.org/badge/latestdoi/31598374)


## Installation

```bash
pip install structure-threader
```

*Structure_threader* is available on
[PyPI](https://pypi.python.org/pypi/structure-threader/). It can be
installed by simply running the above command. If you are on a \*nix like
platform, you can use the `--user` option if you can't or don't want to install
the program as `root` user. Binaries for Structure, fastStructure and
*MavericK* are also distributed for GNU/Linux and macOS. Please note that the macOS binaries included are compiled for x64 and not ARM64, so it will require [Rosetta 2](https://support.apple.com/102527) for Mac computers with Apple silicon. For more details,
please [check the
manual](https://structure-threader.readthedocs.io/en/latest/install/).


## Manual
The complete documentation can be found on [readthedocs.org](https://structure-threader.readthedocs.io/en/latest/).


## Citation
If you use *Structure_threader*, please cite our
~~[Zenodo DOI](https://zenodo.org/badge/latestdoi/31598374).~~
[Molecular Ecology Resources paper](https://doi.org/10.1111/1755-0998.12702)

### Full citation:
<div class="csl-bib-body" style="line-height: 2; margin-left: 2em; text-indent:-2em;">
  <div class="csl-entry">Pina-Martins, F., Silva, D. N., Fino, J., &amp; Paulo, O. S. (2017). Structure_threader: An improved method for automation and parallelization of programs structure, fastStructure and MavericK on multicore CPU systems. <i>Molecular Ecology Resources</i>, n/a-n/a. doi:10.1111/1755-0998.12702</div>
  <span class="Z3988" title="url_ver=Z39.88-2004&amp;ctx_ver=Z39.88-2004&amp;rfr_id=info%3Asid%2Fzotero.org%3A2&amp;rft_id=info%3Adoi%2F10.1111%2F1755-0998.12702&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&amp;rft.genre=article&amp;rft.atitle=Structure_threader%3A%20An%20improved%20method%20for%20automation%20and%20parallelization%20of%20programs%20structure%2C%20fastStructure%20and%20MavericK%20on%20multicore%20CPU%20systems&amp;rft.jtitle=Molecular%20Ecology%20Resources&amp;rft.stitle=Mol%20Ecol%20Resour&amp;rft.aufirst=Francisco&amp;rft.aulast=Pina-Martins&amp;rft.au=Francisco%20Pina-Martins&amp;rft.au=Diogo%20N.%20Silva&amp;rft.au=Joana%20Fino&amp;rft.au=Oct%C3%A1vio%20S.%20Paulo&amp;rft.date=2017-09-16&amp;rft.pages=n%2Fa-n%2Fa&amp;rft.spage=n%2Fa&amp;rft.epage=n%2Fa&amp;rft.issn=1755-0998&amp;rft.language=en"></span>
</div>

## License
This project is licensed under the [GNU General Public License, version 3](https://gitlab.com/StuntsPT/Structure_threader/-/raw/master/LICENSE).
