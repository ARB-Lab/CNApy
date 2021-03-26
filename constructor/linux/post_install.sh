#!/bin/sh
source $PREFIX/etc/profile.d/conda.sh
conda activate $PREFIX

conda install -v -c cnapy/label/test -c conda-forge -c bioconda cnapy --yes
conda clean --all --yes
project_downloader