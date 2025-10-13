GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=4G:ngpus=1"
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.37.2"

INPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/text-archive_ja/sampling/"
OUTPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/toxic-archive_ja/sampling/"

# month="2017-09"
# echo "Processing month: $month"
# qsub ${GPUQOPTS} -N set_${month}_toxic_label -k doe -j oe -o ./log/set_toxic_label -v DOCKER_IMAGE=${DOCKER_IMAGE},INPUT_PATH=${INPUT_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} set_month_toxic_label.sh
months=($(ls $INPUT_PATH | sed 's/\.jsonl$//'))
for month in "${months[@]}"; do
  echo "Processing month: $month"
  qsub ${GPUQOPTS} -N set_${month}_toxic_label -k doe -j oe -o ./log/set_toxic_label -v DOCKER_IMAGE=${DOCKER_IMAGE},INPUT_PATH=${INPUT_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} set_month_toxic_label.sh
done
