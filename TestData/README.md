# Test Data for  *Structure_threader*

In this directory you will find the data that was used to benchmark *Structure_threader*.

## Contents (in alphabetical order):

* BigTestData.str.tar.xz
* extraparams
* joblist.txt
* mainparams
* SmallData.structure.tar.xz

### BigTestData.str.tar.xz

This file is a fastStructure formatted input file which was used to benchmark fastStructure. This is a large SNP file (604 SNPs) which was obtained from the [1000 genomes project](http://www.1000genomes.org). The file was downloaded from [chromossome 22](http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz), and was then filtered using vcftools with the following criteria:

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
However, in order to produce a smaller file than BigTestData.str, the following commands were used for file reduction:

    cut -d " " -f 1-302 SmallData.structure > SmallData302SNPs.structure
    head -n 501 SmallData302SNPs.structure > SmallTestData.structure
    tar cvfJ SmallTestData.structure.tar.xz SmallTestData.structure


### extraparams and mainparams

The STRUCTURE paramater files that were used in the benchmarking process.

### joblist.txt

The joblist used to benchmark *ParallelStructure*. Consists of 16 jobs, 4 values of "K" with 4 replicates each.

### SmallData.structure.tar.xz

This file is a Structure formatted input file which was used to benchmark Structure. This is a medium sized SNP file (302 SNPs) which was obtained from the [1000 genomes project](http://www.1000genomes.org). The file was downloaded from [chromossome 22](http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz), and was then filtered using vcftools following the same criteria and commands as the BigTestData.str file.


The used commands were:

    cut -d " " -f 1-604 BigData.str > BigData604SNPs.str
    head -n 1002 BigData604SNPs.str > BigTestData.str
    tar cvfJ BigTestData.str.tar.xz BigTestData.str
