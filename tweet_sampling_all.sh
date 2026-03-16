#!/bin/sh

QSUBOPTS="-q wLrchq -l select=1:ncpus=8:ngpus=0:mem=64G -v SINGULARITY_IMAGE=imc.tut.ac.jp/transformers-pytorch-cuda118:4.46.3"
BASEDIR=/work/my016/mirror/twitter-stream/sample-archive-twitterstream
DSTDIR=sampled-ja

generate_command(){
	srcdir=${1}
	dstfile=${2}
	workdir=`pwd`
	cat <<EOF
cd ${workdir} && \
source .venv/bin/activate && \
time python3 twitter-sampling.py \
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
	qsub ${QSUBOPTS} -N twitter-sampling-${month} -k doe -j oe
	sleep 15
done
