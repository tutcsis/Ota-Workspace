GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=4G:ngpus=1"
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.37.2"

INPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/1000-toxic-sampling-user_add/"
OUTPUT_PATH="/work/s245302/Ota-Workspace/src/twitter_stream/tweets_group_analysis/tables/toxic_users/"

months=($(ls $INPUT_PATH | sed 's/\.jsonl$//'))
for month in "${months[@]}"; do
  if [ -f "${OUTPUT_PATH}/${month}.jsonl" ]; then
    echo "Output for month ${month} already exists. Skipping..."
    continue
  fi
  echo "Processing month: $month"
  qsub ${GPUQOPTS} -N ${month}_run_1 -k doe -j oe -o ./log/run_1 -v DOCKER_IMAGE=${DOCKER_IMAGE},INPUT_PATH=${INPUT_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} run_1.sh
done
