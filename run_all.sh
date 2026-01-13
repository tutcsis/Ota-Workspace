GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=16G:ngpus=1:vnode="
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.37.2"

ALL_LANG_ARCHIVE="/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive-twitterstream/"
TABLE_DIR="/work/s245302/Ota-Workspace/tables/check_ja_tweets/"

months=($(ls $ALL_LANG_ARCHIVE))
nodes=("xsnd03" "xsnd04" "xsnd05" "xsnd06" "xsnd07")
counter=0
for month in "${months[@]}"; do
  echo "Processing month: $month"
  if [ -f "${TABLE_DIR}/${month}.txt" ]; then
    echo "Table for month ${month} already exists. Skipping..."
    continue
  fi
  qsub ${GPUQOPTS}${nodes[counter]} -N run_${month} -k doe -j oe -o ./log/run_all -v DOCKER_IMAGE=${DOCKER_IMAGE},month=${month} run_month.sh
  counter=$((counter + 1))
  if [ $counter -ge ${#nodes[@]} ]; then
    counter=0
  fi
done
