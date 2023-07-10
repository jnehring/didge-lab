#!/bin/bash

# ./usrun.sh -p batch -c 32 --time 48:00:00 --mem 32GB  /netscratch/nehring/projects/music/didge-lab/slurm/run_sintra.sh

cd "$(dirname "$0")"
cd ../src

export PIP_INDEX_URL=http://pypi-cache/index
export PIP_TRUSTED_HOST=pypi-cache
export PIP_NO_CACHE=true

pip install -r requirements.txt

cd cad/cadsd
python setup.py build_ext --inplace

cd ../../

python -m cad.evo.evolve_nazare -n_threads 128
