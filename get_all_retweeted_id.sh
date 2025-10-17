#PBS -q gLrchq
#PBS -l select=1:ncpus=4:mem=4G:ngpus=1
#PBS -v SINGULARITY_IMAGE=imc.tut.ac.jp/transformers-pytorch-cuda118:4.46.3
#PBS -k doe -j oe -o ./log

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

INPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/"
RETWEET_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/ja_retweet_ids/"
TWEET_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/ja_tweet_ids/"

months=($(ls $INPUT_PATH))
for month in "${months[@]}"; do
  echo "Processing month: $month"
  time uv run python src/twitter_stream/get_retweeted_id.py \
    --input_path ${INPUT_PATH}${month}/ \
    --retweet_ids_path ${RETWEET_PATH} \
    --tweet_ids_path ${TWEET_PATH} \
    --month ${month}
  # break
done

mv "./log/${PBS_JOBID}.OU" "./log/${PBS_JOBNAME}.o${PBS_JOBID%.xregistry*}"
