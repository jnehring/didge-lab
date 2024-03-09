#!/bin/bash

export PIP_INDEX_URL=http://pypi-cache/index
export PIP_TRUSTED_HOST=pypi-cache
export PIP_NO_CACHE=true

cd /netscratch/nehring/projects/music/didgelab2/src

pip install -r requirements.txt

cd didgelab/calc/sim
python setup.py build_ext --inplace
