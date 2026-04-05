FROM mambaorg/micromamba:1.5.8

ARG ENV_NAME=alstructure

USER $MAMBA_USER

RUN micromamba config set channel_priority strict

# Install core environment (ONLY stable conda packages)
RUN micromamba create -y -n ${ENV_NAME} \
    r-base=4.3 \
    r-rcolorbrewer \
    r-devtools \
    r-svd \
    bioconductor-snprelate \
    bioconductor-lfa \
    -c conda-forge -c bioconda \
    && micromamba run -n ${ENV_NAME} Rscript -e '\
        devtools::install_github("storeylab/alstructure@e3554111e746a2359675d6615459af8579b69a14", \
                                build_vignettes=FALSE, upgrade="never")' \
    && micromamba clean --all --yes

ENV PATH=/opt/conda/envs/${ENV_NAME}/bin:$PATH
