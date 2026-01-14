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

ALL_LANG_TW="data/twitter_stream/sample-archive-twitterstream/"
STR_JA_TW="data/twitter_stream/sample-archive_str_ja1/"
STR_JA2_TW="data/twitter_stream/sample-archive_str_ja2/"
# month="2017-02"
echo "month=${month}"
mkdir -p ${STR_JA_TW}${month}
mkdir -p ${STR_JA2_TW}${month}

for file in "${ALL_LANG_TW}${month}/"*; do
	if [ -f "$file" ]; then
		ja1_file="${STR_JA_TW}${month}/$(basename "$file")"
		ja2_file="${STR_JA2_TW}${month}/$(basename "$file")"
		grep '"lang":"ja"' $file > "$ja1_file"
		time uv run python src/twitter_stream/filter_ja_tweets.py \
			--ja1_file ${ja1_file} \
			--ja2_file ${ja2_file}
	fi
done
echo "Extracted Japanese tweets to ${STR_JA_TW}"

mv "./log/get_all_ja_tw_data/${PBS_JOBID}.OU" "./log/get_all_ja_tw_data/${PBS_JOBNAME}.o${PBS_JOBID%.xregistry*}"

