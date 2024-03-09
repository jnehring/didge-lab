
srun -K \
  --container-mounts=/netscratch:/netscratch,/ds:/ds,$HOME:$HOME \
  --container-workdir=$HOME \
  --container-image=/netscratch/enroot/nvcr.io_nvidia_pytorch_22.03-py3.sqsh \
  --ntasks=1 \
  --nodes=1 \
  -p batch \
  --pty \
  --gpus=0 \
  --time 08:00:00 \
  /bin/bash

