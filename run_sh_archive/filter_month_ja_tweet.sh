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

echo ARCHIVE_PATH=${ARCHIVE_PATH}
echo OUTPUT_PATH=${OUTPUT_PATH}
echo month=${month}

mkdir -p ${OUTPUT_PATH}${month}
files=($(for f in ${ARCHIVE_PATH}${month}/*.txt; do basename "$f"; done))
for file in "${files[@]}"; do
  INPUT_FILE=${ARCHIVE_PATH}${month}/${file}
  JA_FILE=${OUTPUT_PATH}${month}/${file}
  echo "file: ${file}"
  time grep -F '"lang":"ja"' ${INPUT_FILE} | grep -v '"lang":"ja".*"lang":"ja"' > ${JA_FILE}
  # sh filter_ja_tweet.sh ${INPUT_FILE} ${JA_FILE}
done
mv "./log/filter_ja_tweet/${PBS_JOBID}.OU" "./log/filter_ja_tweet/${PBS_JOBNAME}.o${PBS_JOBID%.xregistry*}"
