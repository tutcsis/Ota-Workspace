DATA_PATH="data/twitter_stream/ja_tweet_ids/"
OUTPUT_FILE="tables/ja_tweet_counts.csv"
MONTHS_FILE=($(ls $DATA_PATH))

echo "**comments** output_file: $OUTPUT_FILE"
echo "month,tweets" >> $OUTPUT_FILE
for month_file in "${MONTHS_FILE[@]}"; do
  echo "**comments** file_name: $month_file"
  echo "${month_file%.txt},$(wc -l < ${DATA_PATH}${month_file})" >> $OUTPUT_FILE
done
