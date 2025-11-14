from pathes import (
  TOXIC_TWEET_PATH,
  NEW_TOXIC_TW_COUNT_PATH,
  TOXIC_LABEL,
  USE_YEARS,
  GROUP
)
import utils
import os
import json
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
  data_path: str = TOXIC_TWEET_PATH
  table_path: str = NEW_TOXIC_TW_COUNT_PATH
  table_columns: list = ['1', '2', 'all']
  toxic_label: list = TOXIC_LABEL
  years: list = USE_YEARS
  groups: list = GROUP

def labeling_tw_len(tw_length):
  if tw_length >= 10 and tw_length <= 80:
    return '1'
  elif tw_length >= 81:
    return '2'
  return None

def main(args):
  # init dataframes
  twlen_df_dict = dict()
  for toxic in args.toxic_label:
    twlen_df_dict[toxic] = pd.DataFrame(
      columns=args.table_columns
    )

  # set group by twlen
  # group1: 10 <= twlen <= 80
  # group2: 81 <= twlen <= Infinity
  for file in utils.get_file_names(args.data_path):
    data_file = os.path.join(args.data_path, file)
    month = file.replace('.jsonl', '')
    print(f"data_file: {data_file}")
    for toxic in args.toxic_label:
      twlen_df_dict[toxic].loc[month] = 0

    with open(data_file, 'r') as f:
      for line in f:
        tw_json = json.loads(line)
        tw_length = len(tw_json['text'])
        for toxic in args.toxic_label:
          curr_len_label = labeling_tw_len(tw_length)
          if curr_len_label and tw_json[toxic] == 1:
            twlen_df_dict[toxic].at[month, curr_len_label] += 1

    for toxic in args.toxic_label:
      twlen_df_dict[toxic].at[month, 'all'] = twlen_df_dict[toxic].loc[month].sum()
    print(f"{month} finished!!")

  for toxic in args.toxic_label:
    print(f"{toxic} df: {twlen_df_dict[toxic]}")
    twlen_df_dict[toxic].to_csv(f"{args.table_path}{toxic}.csv")

if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
