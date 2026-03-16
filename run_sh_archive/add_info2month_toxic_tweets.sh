cd ${PBS_O_WORKDIR}

TORCH_HOME=/work/${LOGNAME}/.cache/torch
TRANSFORMERS_CACHE=/work/${LOGNAME}/.cache/transformers
HF_HOME=/work/${LOGNAME}/.cache/huggingface
UV_CACHE_DIR=/work/${LOGNAME}/.cache/uv
PIP_CACHE_DIR=/work/${LOGNAME}/.cache/pip
TRITON_CACHE_DIR=/work/${LOGNAME}/.cache/triton
export TORCH_HOME TRANSFORMERS_CACHE HF_HOME UV_CACHE_DIR PIP_CACHE_DIR TRITON_CACHE_DIR

#ADHOC FIX to avoid "undefined symbol: cuModuleGetFunction" error.
export TRITON_LIBCUDA_PATH=/usr/local/cuda/lib64/stubs

#ADHOC FIX to avoid torch._inductor.exc.InductorError
#For more detail, see https://github.com/pytorch/pytorch/issues/119054
export TRITON_PTXAS_PATH=/usr/local/cuda/bin/ptxas

export TORCH_USE_CUDA_DSA=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

source .venv/bin/activate

echo TOXIC_TWEET_PATH=${TOXIC_TWEET_PATH}
echo ALL_DATA_PATH=${ALL_DATA_PATH}
echo ADDED_TWEET_PATH=${ADDED_TWEET_PATH}
echo month=${month}

time uv run python src/twitter_stream/add_info2toxic_tweets.py \
  --toxic_tweets ${TOXIC_TWEET_PATH} \
  --all_data_path ${ALL_DATA_PATH} \
  --output_tweets ${ADDED_TWEET_PATH} \
  --month ${month}

mv "./log/add_info2toxic_tweets/${PBS_JOBID}.OU" "./log/add_info2toxic_tweets/${PBS_JOBNAME}.o${PBS_JOBID%.xregistry*}"
