#!/bin/sh

# ./usrun.sh -p batch --gpus=1 --time 08:00:00 /netscratch/nehring/projects/diss/mds-testbed/mds-testbed/slurm/init_server.sh full_experiment bert-base-uncased

export PIP_INDEX_URL=http://pypi-cache/index
export PIP_TRUSTED_HOST=pypi-cache
export PIP_NO_CACHE=true

export TORCH_HOME=/netscratch/nehring/cache/torch
export HF_HOME=/netscratch/nehring/cache/huggingface
export TRANSFORMERS_CACHE=/netscratch/nehring/cache/transformers

cd /netscratch/nehring/projects/diss/mds-testbed/mds-testbed
pip install -r requirements.txt
cd src

if [ $1 = "hyperparameter-bert" ]; then
    python3 -m experiments.models.train --experiment search_hyperparameter --model_name_or_path bert-base-uncased --dataset_type small  --dataset_path ../data/final_data_small
elif [ $1 = "hyperparameter-history" ]; then
    python3 -m experiments.models.train --experiment search_hyperparameter --model_name_or_path history --dataset_type small  --dataset_path ../data/final_data_small
elif [ $1 = "hyperparameter-conf" ]; then
    python3 -m experiments.models.train --experiment search_hyperparameter --model_name_or_path confidence --dataset_type small  --dataset_path ../data/final_data_small
elif [ $1 = "hyperparameter-roberta" ]; then
    python3 -m experiments.models.train --experiment search_hyperparameter --model_name_or_path roberta-base --dataset_type small  --dataset_path ../data/final_data_small
elif [ $1 = "hyperparameter-distilbert" ]; then
    python3 -m experiments.models.train --experiment search_hyperparameter --model_name_or_path distilbert-base-uncased --dataset_type small  --dataset_path ../data/final_data_small
elif [ $1 = "full_experiment" ]; then

    python -m experiments.models.generate_starter_scripts | grep "model_name_or_path $2" | while read line 
    do
        eval "$line"
    done
fi

