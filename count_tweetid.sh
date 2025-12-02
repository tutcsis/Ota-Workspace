
# ja
# DATA_PATH="data/twitter_stream/ja_tweet_ids/"
# OUTPUT_FILE="tables/ja_tweet_counts.csv"
# MONTHS_FILE=($(ls $DATA_PATH))

# echo "**comments** output_file: $OUTPUT_FILE"
# echo "month,tweets" >> $OUTPUT_FILE
# for month_file in "${MONTHS_FILE[@]}"; do
# 	echo "**comments** file_name: $month_file"
# 	echo "${month_file%.txt},$(wc -l < ${DATA_PATH}${month_file})" >> $OUTPUT_FILE
# done

# all_lang
DATA_PATH="data/twitter_stream/sample-archive-twitterstream/"
OUTPUT_FILE="tables/all_lang_tweet_counts.csv"

MONTHES_FOLDER=($(ls $DATA_PATH))
echo "**comments** output_file: $OUTPUT_FILE"
echo "month,alltweets" >> $OUTPUT_FILE
for month_folder in "${MONTHES_FOLDER[@]}"; do
	echo "**comments** folder_name: $month_folder"
	month_path="${DATA_PATH}${month_folder}/"
	month_files=($(ls $month_path))
	total_count=0
	for month_file in "${month_files[@]}"; do
		echo "**comments** file_name: $month_file"
		count=$(wc -l < "${month_path}${month_file}")
		total_count=$((total_count + count))
	done
	echo "${month_folder},${total_count}" >> $OUTPUT_FILE
done

