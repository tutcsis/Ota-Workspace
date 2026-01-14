GPUQOPTS="-q gLrchq -l select=1:ncpus=1:mem=16G:ngpus=1:vnode="
DOCKER_IMAGE="imc.tut.ac.jp/transformers-pytorch-cuda118:4.37.2"

ALL_LANG_TW="data/twitter_stream/sample-archive-twitterstream/"

months=($(ls $ALL_LANG_TW))
nodes=("xsnd02" "xsnd03" "xsnd04" "xsnd05" "xsnd06" "xsnd07" "xsnd08" "xsnd09" "xsnd10" "xsnd11")
counter=0
for month in "${months[@]}"; do
  echo "Processing month: $month"
  qsub ${GPUQOPTS}${nodes[counter]} -N run_${month} -k doe -j oe -o ./log/get_all_ja_tw_data -v DOCKER_IMAGE=${DOCKER_IMAGE},month=${month} get_ja_tw_data.sh
  counter=$((counter + 1))
  if [ $counter -ge ${#nodes[@]} ]; then
    counter=0
  fi
done
