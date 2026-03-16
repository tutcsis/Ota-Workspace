#!/bin/sh

QSUBOPTS="-q wLrchq -l select=1:ncpus=8:ngpus=0:mem=64G -v SINGULARITY_IMAGE=imc.tut.ac.jp/transformers-pytorch-cuda118:4.46.3"
BASEDIR=/work/my016/mirror/twitter-stream/sample-archive-twitterstream
DSTDIR=/work/s245302/Ota-Workspace/data/twitter_stream/sampled-ja-0_001

generate_command(){
	srcdir=${1}
	dstfile=${2}
	workdir=`pwd`
	cat <<EOF
cd ${workdir} && \
source .venv/bin/activate && \
time python3 src/twitter_stream/new_group_analyze/0-1_filter_ja_sampling.py \
  --srcdir=${srcdir} \
  --output=${dstfile} \
  --num_processes=8 \
  --language=ja \
  --ratio=0.01
EOF
}

if [ ! -d ${DSTDIR} ]
then
	mkdir ${DSTDIR}
fi

for srcdir in ${BASEDIR}/20*
do
	month=`basename ${srcdir}`
	generate_command ${srcdir} ${DSTDIR}/${month}.jsonl |\
	qsub ${QSUBOPTS} -N twitter-sampling-${month} -k doe -j oe -o ./log/twitter_sampling
	sleep 15
done
