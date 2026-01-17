GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=16G:ngpus=1:vnode="
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.37.2"

INPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample_1percent_ja/"
OUTPUT_PATH="/work/s245302/Ota-Workspace/data/twitter_stream/sample_1percent_toxic_ja/"

months=($(ls $INPUT_PATH | sed 's/\.jsonl$//'))
nodes=("xsnd03" "xsnd04" "xsnd05" "xsnd06" "xsnd07")
counter=0
for month in "${months[@]}"; do
  if [ -f "${OUTPUT_PATH}/${month}.jsonl" ]; then
    echo "Output for month ${month} already exists. Skipping..."
    continue
  fi
  echo "Processing month: $month"
  qsub ${GPUQOPTS}${nodes[counter]} -N set_${month}_1000toxic_label_media -k doe -j oe -o ./log/sample_1percent_toxic_ja_all -v DOCKER_IMAGE=${DOCKER_IMAGE},INPUT_PATH=${INPUT_PATH},OUTPUT_PATH=${OUTPUT_PATH},month=${month} set_month_toxic_label.sh
  counter=$((counter + 1))
  if [ $counter -ge ${#nodes[@]} ]; then
    counter=0
  fi
done
