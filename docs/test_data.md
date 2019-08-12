# Test Data for  *Structure_threader*
In [this directory](https://github.com/StuntsPT/Structure_threader/tree/master/TestData) you will find the data that was used to benchmark *Structure_threader*.


## BigTestData.str.tar.xz
This file is a *fastStructure* formatted input file which was used to benchmark *fastStructure*. This is a large SNP file (1000 SNPs across 1000 individuals) which was obtained from the [1000 genomes project](http://www.1000genomes.org). The file was downloaded from [chromossome 22](http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz), and was then filtered using [vcftools](https://github.com/vcftools/vcftoolshttps://github.com/vcftools/vcftools) with the following criteria:

* only biallelic, non-singleton SNV sites
* SNvs must be at lest 2KB apart from each other
* minor allele frequency < 0.05

The used command was:

    ./vcftools --gzvcf \
    ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
    --maf 0.05 --thin 2000 --min-alleles 2 --max-alleles 2 --non-ref-ac 2 \
    --recode --chr 22 --out Chr22

This was the criteria that was used on the *admixture* [analysis of the 1000 genomes project](http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/supporting/admixture_files/README.admixture_20141217).

The file was then converted to structure format with [PGDSpider](http://www.cmpg.unibe.ch/software/PGDSpider/).
To further reduce the dataset (for faster benchmarking), the file was then processed with `cut` and `head` and finally compressed with xz.

The used commands were:

    cut -d " " -f 1-1000 Chr22.recode.str | head -n 2000 > BigTestData.str
    tar cvfJ BigTestData.str.tar.xz BigTestData.str


## BigTestData.bed.tar.xz
This file is a *PLINK* formatted `.bed`, `.bim` and `.fam` set of files. They were obtained in the exact same way as `BigTestData.str.tar.xz`, except for the conversion using *PGDSPIDER*, which was not used. Instead, the filtered VCF file was reduced to 501 individuals and 1000 SNPs with the following command:

    head -n 1253 Chr22.recode.vcf |cut -f 1-510 > Testdata.vcf

This file was then converted to the *PLINK* format and compressed with the following commands:

    plink1.9 --vcf Testdata.vcf
    mv plink.bed BigTestData.bed
    mv plink.fam BigTestData.fam
    mv plink.bim BigTestData.bim
    tar cvfJ BigTestData.bed.tar.xz BigTestData.bed BigTestData.fam BigTestData.bim


## BigTestData.vcf.tar.xz
    This file is *VCF* formatted. It was obtained in the exact same way as `BigTestData.str.tar.xz`, except for the conversion using *PGDSPIDER*, which was not used. Instead, the filtered VCF file was reduced to 501 individuals and 1000 SNPs and compressed with the following command:

        head -n 1253 Chr22.recode.vcf |cut -f 1-510 > BigTestData.vcf
        tar cvfJ BigTestData.vcf.tar.xz BigTestData.vcf


## extraparams and mainparams
The *STRUCTURE* parameter files that were used in the benchmarking process.


## joblist.txt
The joblist used to benchmark *ParallelStructure*. Consists of 16 jobs, 4 values of "K" with 4 replicates each.


## SmallTestData.structure
This file is a Structure formatted input file which was used to benchmark STRUCTURE and *MavericK*. This is a medium sized SNP file (80 SNPs) which was obtained from the [1000 genomes project](http://www.1000genomes.org). The file was downloaded from [chromossome 22](http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz), and was then filtered using vcftools following the same criteria and commands as the BigTestData.str file.


The used commands were:

    cut -d " " -f 1-80 SmallData.structure > SmallData302SNPs.structure
    head -n 201 SmallData302SNPs.structure > SmallTestData.structure


## parameter.txt
    The *MavericK* parameter file that is used in the unit tests.


## mav_benchmark_parameters
    The file with the *MAvericK* benchmark parameters.
