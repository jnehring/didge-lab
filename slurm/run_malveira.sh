#!/bin/bash

export PIP_INDEX_URL=http://pypi-cache/index
export PIP_TRUSTED_HOST=pypi-cache
export PIP_NO_CACHE=true

cd "$(dirname "$0")"
cd ../src

pip install -r requirements.txt

cd cad/cadsd
python setup.py build_ext --inplace

cd ../../

python -m cad.evo.evolve_malveira -n_threads 128