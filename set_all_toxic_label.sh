GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=4G:ngpus=1"
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.37.2"

INPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/1000-sampling-user_add/"
OUTPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/1000-toxic-sampling-user_add/"
# INPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/text-archive_ja/sampling/"
# OUTPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/toxic-archive_ja/sampling/"

# month="2017-09"
# echo "Processing month: $month"
# qsub ${GPUQOPTS} -N set_${month}_toxic_label -k doe -j oe -o ./log/set_toxic_label -v DOCKER_IMAGE=${DOCKER_IMAGE},INPUT_PATH=${INPUT_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} set_month_toxic_label.sh
months=($(ls $INPUT_PATH | sed 's/\.jsonl$//'))
for month in "${months[@]}"; do
  if [ -f "${OUTPUT_PATH}/${month}.jsonl" ]; then
    echo "Output for month ${month} already exists. Skipping..."
    continue
  fi
  echo "Processing month: $month"
  qsub ${GPUQOPTS} -N set_${month}_1000toxic_label -k doe -j oe -o ./log/set_1000toxic_label -v DOCKER_IMAGE=${DOCKER_IMAGE},INPUT_PATH=${INPUT_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} set_month_toxic_label.sh
  # qsub ${GPUQOPTS} -N set_${month}_toxic_label -k doe -j oe -o ./log/set_toxic_label -v DOCKER_IMAGE=${DOCKER_IMAGE},INPUT_PATH=${INPUT_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} set_month_toxic_label.sh
done
