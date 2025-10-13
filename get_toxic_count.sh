DATA_PATH="data/twitter_stream/toxic-archive_ja/sampling/"
OUTPUT_FILE="tweet_toxic_count.csv"
MONTHS_FILE=($(ls $DATA_PATH))
categories=("personal" "others" "illegal" "corporate" "violent" "discriminatory" "obscene")

# csv header
echo "Toxic counts have been written to $OUTPUT_FILE"
echo -n "month" > $OUTPUT_FILE
for category in "${categories[@]}"; do
  echo -n ",$category" >> $OUTPUT_FILE
done
echo -n ",total" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE


for month_file in "${MONTHS_FILE[@]}"; do
  echo "Processing file: $month_file"

  echo -n "${month_file%.jsonl}" >> $OUTPUT_FILE

  for category in "${categories[@]}"; do
    count=$(cat ${DATA_PATH}${month_file} | jq -r "select(.$category == 1) | .$category" | wc -l)
    echo -n ",$count" >> $OUTPUT_FILE
  done
  echo -n ",$(wc -l < ${DATA_PATH}${month_file})" >> $OUTPUT_FILE
  echo "" >> $OUTPUT_FILE
done
