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

echo INPUT_PATH=${INPUT_PATH}
echo OUTPUT_PATH=${OUTPUT_PATH}
echo month=${month}

mkdir -p ${OUTPUT_PATH}${month}
files=($(for f in ${INPUT_PATH}${month}/*.txt; do basename "$f"; done))
for file in "${files[@]}"; do
  INPUT_FILE=${INPUT_PATH}${month}/${file}
  OUTPUT_FILE=${OUTPUT_PATH}${month}/${file%.txt}.json
  echo "file: ${file}"
  time uv run python src/twitter_stream/get_tweet.py \
    --data_path ${INPUT_FILE} \
    --out_path ${OUTPUT_FILE}
done
mv "./log/get_ja_tweet_text/${PBS_JOBID}.OU" "./log/get_ja_tweet_text/${PBS_JOBNAME}.o${PBS_JOBID%.xregistry*}"
