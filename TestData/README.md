#Test Data for  *Structure_threader*

In this directory you will find the data that was used to benchmark *Structure_threader*.

##Contents (in alphabetical order):

* Chr1.str.tar.xz
* Chr22.str.tar.xz
* benchmark.sh
* extraparams
* joblist.txt
* mainparams
* TestData.structure

###Chr1.str.tar.xz

This file is a fastStructure formatted input file which was used to benchmark fastStructure. This is a **huge** SNP file (16854 SNPs) which was obtained from the [1000 genomes project](http://www.1000genomes.org). The file was downloaded from [here](ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr1.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz), and was then filtered using vcftools with the following criteria:

* only biallelic, non-singleton SNV sites
* SNvs must be at lest 2KB apart from each other
* minor allele frequency < 0.05

The used command was:

./vcftools --gzvcf
ALL.chr1.phase3_shapeit2_mvncall_integrated_v4.20130502.genotypes.vcf.gz
--maf 0.05 --thin 2000 --min-alleles 2 --max-alleles 2 --non-ref-ac 2 --recode --chr 1 --out Chr1

This was the criteria that was used on the *admixture* [analysis of the 1000 genomes project](ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/supporting/admixture_files/README.admixture_20141217).

The file was then converted to structure format with [PGDSpider](http://www.cmpg.unibe.ch/software/PGDSpider/), and compressed with xz.

###Chr22.str.tar.xz

This file is similar to the one above, but it is from [chromossome 22](ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz) instead of chromossome 1. As such it contains fewer SNPs (2719).

The file processing was done in the same way as for Chr1.

###extraparams and mainparams

The STRUCTURE paramater files that were used in the benchmarking process.

###joblist.txt

The joblist used to benchmark *ParallelStructure*. Consists of 16 jobs, 4 values of "K" with 4 replicates each.

###TestData.structure

This is the datafile itself  that was used in the benchmarking process.
It contains 83 individuals, divided in 17 populations, represented for 29 SNP loci.
There is aproximately 13% missing data in the file.
