GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=4G:ngpus=1"
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.37.2"

INPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/"
OUTPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/text-archive_ja/"

# month="2017-09"
# echo "Processing month: $month"
# qsub ${GPUQOPTS} -N get_${month}_ja_tweet_text -k doe -j oe -o ./log/get_ja_tweet_text -v DOCKER_IMAGE=${DOCKER_IMAGE},INPUT_PATH=${INPUT_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} get_month_ja_tweet_text.sh
months=($(ls $INPUT_PATH))
for month in "${months[@]}"; do
  echo "Processing month: $month"
  qsub ${GPUQOPTS} -N get_${month}_ja_tweet_text -k doe -j oe -o ./log/get_ja_tweet_text -v DOCKER_IMAGE=${DOCKER_IMAGE},INPUT_PATH=${INPUT_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} get_month_ja_tweet_text.sh
done
