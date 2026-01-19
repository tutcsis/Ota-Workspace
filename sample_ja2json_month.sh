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

INPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sampled-ja-0_001/"
OUTPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sampled_ja2json-0_001/"
# INPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/"
# OUTPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample_0_1percent_ja/"

echo "month=${month}"
time uv run python src/twitter_stream/sample_ja2json.py \
  --dataset_path ${INPUT_PATH}${month}.jsonl \
  --output_path ${OUTPUT_PATH} \
  --month ${month}

mv "./log/sample_ja2json/${PBS_JOBID}.OU" "./log/sample_ja2json/${PBS_JOBNAME}.o${PBS_JOBID%.xregistry*}"
