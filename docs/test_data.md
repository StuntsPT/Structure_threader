# Test Data for  *Structure_threader*
In the [*tests/data/* directory](https://gitlab.com/StuntsPT/Structure_threader/-/tree/master/tests/data) you will find the data that was used to benchmark *Structure_threader*, some of which is also currently used for unit testing.


## BigTestData.str.tar.xz
This file is a *fastStructure* formatted input file which is used for the *fastStructure* unit tests. This is a large SNP file (1000 SNPs across 500 individuals) which was obtained from the [1000 genomes project](http://www.1000genomes.org). The file was downloaded from [chromossome 22](https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz), and was then filtered using [vcftools](https://github.com/vcftools/vcftools) with the following criteria:

* only biallelic, non-singleton SNV sites
* SNVs must be at lest 2KB apart from each other
* minor allele frequency < 0.05

The used command was:

    vcftools --gzvcf \
    ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz \
    --maf 0.05 --thin 2000 --min-alleles 2 --max-alleles 2 --non-ref-ac 2 \
    --recode --chr 22 --out Chr22

This was the criteria that was used on the *admixture* [analysis of the 1000 genomes project](http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/supporting/admixture_files/README.admixture_20141217).

The file was then converted to structure format with [PGDSpider](http://www.cmpg.unibe.ch/software/PGDSpider/). The settings used for generating the SPID conversion file were the following:

* Default options on the VCF input tab
* On the STRUCTURE output tab:
    * Save more specific fastSTRUCTURE format? -> Yes
    * Specify which data (...) -> SNPs  

The SPID file is included in the repository with the rest of the test data.  
To further reduce the dataset (for faster benchmarking), the file was then processed with `cut`, `head`, `tail` and `sed` and finally compressed with xz.

The used commands were:

    cut -d " " -f 1-500 Chr22.recode.str | head -n 1004 | tail -n +2 | sed '1d' > BigTestData.str
    tar cvfJ BigTestData.str.tar.xz BigTestData.str


## BigTestData.bed.tar.xz
This file is a *PLINK* formatted `.bed`, `.bim` and `.fam` set of files. They were obtained in the exact same way as `BigTestData.str.tar.xz`, except for the conversion using *PGDSPIDER*, which was not used. Instead, the filtered VCF file was reduced to 501 individuals and 1000 SNPs with the following command:

    head -n 1253 Chr22.recode.vcf | cut -f 1-510 > Testdata.vcf

This file was then converted to the *PLINK* format and compressed with the following commands:

    plink1.9 --vcf Testdata.vcf
    mv plink.bed BigTestData.bed
    mv plink.fam BigTestData.fam
    mv plink.bim BigTestData.bim
    tar cvfJ BigTestData.bed.tar.xz BigTestData.bed BigTestData.fam BigTestData.bim


## BigTestData.pgen.tar.xz
This file is a *PLINK 2* formatted `.pgen`, `.psam` and `.pvar` set of files. They were obtained in the exact same way as `BigTestData.str.tar.xz`, except for the conversion using *PGDSPIDER*, which was not used. Instead, the filtered VCF file was reduced to 501 individuals and 1000 SNPs with the following command:

    head -n 1253 Chr22.recode.vcf | cut -f 1-510 > Testdata.vcf

This file was then converted to the *PLINK 2* format and compressed with the following commands:

    plink2 --vcf Testdata.vcf
    mv plink2.pgen BigTestData.pgen
    mv plink2.psam BigTestData.psam
    mv plink2.pvar BigTestData.pvar
    tar cvfJ BigTestData.pgen.tar.xz BigTestData.pgen BigTestData.psam BigTestData.pvar


## BigTestData.vcf.tar.xz and BigTestData.vcf.gz
These files are *VCF* formatted. They were obtained in the exact same way as `BigTestData.str.tar.xz`, except for the conversion using *PGDSPIDER*, which was not used. Instead, the filtered VCF file was reduced to 501 individuals and 1000 SNPs and compressed with the following commands:

    head -n 1253 Chr22.recode.vcf | cut -f 1-510 > BigTestData.vcf
    tar cvfJ BigTestData.vcf.tar.xz BigTestData.vcf
    gzip BigTestData.vcf


## SmallTestData.structure
This file is a Structure formatted input file which was used to benchmark STRUCTURE and *MavericK*. This is a medium sized SNP file (80 SNPs) which was obtained from the [1000 genomes project](http://www.1000genomes.org). The file was downloaded from [chromossome 22](https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz), and was then filtered using vcftools following the same criteria and commands as the BigTestData.str file.


The used commands were:

    cut -d " " -f 1-80 Chr22.recode.str | head -n 201 | tail -n +2 | sed 's/\t1\t1\t0\t0\textraCol//; s/ /\t/g' > SmallTestData.structure


## Reduced_dataset.structure
This file is a Structure formatted input file which is used in the field tests for STRUCTURE. This is a small sized SNP file (29 SNPs) which was obtained from the [1000 genomes project](http://www.1000genomes.org). The file was downloaded from [chromossome 22](https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz), and was then filtered using vcftools following the same criteria and commands as the BigTestData.str file.

The used commands were:

    cut -d " " -f 1-29 Chr22.recode.str | head -n 70 | tail -n +2 | sed 's/\t1\t1\t0\t0\textraCol//; s/ /\t/g' > Reduced_dataset.structure


## extraparams and mainparams
The *STRUCTURE* parameter files that were used in the benchmarking process.


## parameters.txt
The *MavericK* parameters file that is used in the unit tests.


## nad_popfile.txt
The population file containing each individual's identifier along with its associated population. It was obtained using the [index from the 1000 genomes project](https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000_genomes_project/1000genomes.sequence.index), which was filtered into the popfile using the contents from the indfile, with the following command:

    grep -f indfile.txt 1000genomes.sequence.index | sed 's/ \+/\t/' | cut -f 11,12 | sort -k 2 | uniq | cut -f 2 > popfile.txt

## joblist.txt
The joblist used to benchmark *ParallelStructure*. Consists of 16 jobs, 4 values of "K" with 4 replicates each.


## mav_benchmark_parameters
The file with the *MavericK* benchmark parameters.
