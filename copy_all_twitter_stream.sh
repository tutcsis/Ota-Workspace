GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=4G:ngpus=1"
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.37.2"

DATA_PATH="/work/my016/mirror/twitter-stream/sample-archive-twitterstream/"
OUTPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive-twitterstream/"

months=($(ls $DATA_PATH))
for month in "${months[@]}"; do
  echo "Processing month: $month"
  qsub ${GPUQOPTS} -N copy_${month}_twitter_stream -k doe -j oe -o ./log -v DOCKER_IMAGE=${DOCKER_IMAGE},DATA_PATH=${DATA_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} copy_month_twitter_stream.sh
done
