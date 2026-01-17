GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=32G:ngpus=1:vnode="
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.37.2"

INPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/"
OUTPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample_1percent_ja/"

months=($(ls $INPUT_PATH))
nodes=("xsnd03" "xsnd04" "xsnd05" "xsnd06" "xsnd07")
counter=0
for month in "${months[@]}"; do
  echo "Processing month: $month"
  if [ -f "${OUTPUT_PATH}/${month}.jsonl" ]; then
    echo "Table for month ${month} already exists. Skipping..."
    continue
  fi
  qsub ${GPUQOPTS}${nodes[counter]} -N sample_1percent_ja_all_${month} -k doe -j oe -o ./log/sample_1percent_ja_all -v DOCKER_IMAGE=${DOCKER_IMAGE},month=${month} sample_1percent_ja_month.sh
  counter=$((counter + 1))
  if [ $counter -ge ${#nodes[@]} ]; then
    counter=0
  fi
done
