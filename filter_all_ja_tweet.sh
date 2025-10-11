GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=4G:ngpus=1"
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.37.2"

ARCHIVE_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive-twitterstream/"
OUTPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/"

# month="2017-09"
# echo "Processing month: $month"
# qsub ${GPUQOPTS} -N filter_${month}_ja_tweet -k doe -j oe -o ./log/filter_ja_tweet -v DOCKER_IMAGE=${DOCKER_IMAGE},ARCHIVE_PATH=${ARCHIVE_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} filter_month_ja_tweet.sh
months=($(ls $ARCHIVE_PATH))
for month in "${months[@]}"; do
  echo "Processing month: $month"
  qsub ${GPUQOPTS} -N filter_${month}_ja_tweet -k doe -j oe -o ./log/filter_ja_tweet -v DOCKER_IMAGE=${DOCKER_IMAGE},ARCHIVE_PATH=${ARCHIVE_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} filter_month_ja_tweet.sh
done
