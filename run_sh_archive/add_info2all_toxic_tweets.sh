GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=16G:ngpus=1:vnode=xsnd03"
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.46.3"

TOXIC_TWEET_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/1000-toxic-sampling-user_add/"
ALL_DATA_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/"
ADDED_TWEET_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/1000-toxic-sampling-machine_add/"

months=($(ls $TOXIC_TWEET_PATH | sed 's/\.jsonl$//'))
for month in "${months[@]}"; do
  if [ -f "${ADDED_TWEET_PATH}/${month}.jsonl" ]; then
    echo "Output for month ${month} already exists. Skipping..."
    continue
  fi
  echo "Processing month: $month"
  qsub ${GPUQOPTS} -N add_info${month}_toxic_tweets -k doe -j oe -o ./log/add_info2toxic_tweets -v DOCKER_IMAGE=${DOCKER_IMAGE},TOXIC_TWEET_PATH=${TOXIC_TWEET_PATH},ALL_DATA_PATH=${ALL_DATA_PATH},ADDED_TWEET_PATH=${ADDED_TWEET_PATH},month=${month} add_info2month_toxic_tweets.sh
done
