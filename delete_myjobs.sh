JOBS=($(qstat -u $USER | awk '{print $1}' | grep -o '[0-9]*'))
for JOB in "${JOBS[@]}"; do
	qdel $JOB
done