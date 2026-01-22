import os
import json
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import utils
from pathes import (
  TOXIC_LABEL,
)
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
  data_path: str = "data/twitter_stream/sampled-toxic_ja-0_001/"
  table_path: str = "tables/new_group_analyze/2-2_textlen_group/"
  table_columns: list = ['1', '2', 'all']
  noise_len: int = 10
  labeling_len: int = 80
  toxic_label: list = TOXIC_LABEL

def labeling_tw_len(tw_length):
  if tw_length >= args.noise_len and tw_length <= args.labeling_len:
    return '1'
  elif tw_length >= args.labeling_len + 1:
    return '2'
  return None

def main(args):
  # init dataframes
  twlen_df_dict = dict()
  for toxic in args.toxic_label:
    twlen_df_dict[toxic] = pd.DataFrame(
      columns=args.table_columns
    )
  twlen_df_dict['all']  = pd.DataFrame(
    columns=args.table_columns
  )

  # set group by twlen
  # group1: 10 <= twlen <= 80
  # group2: 81 <= twlen <= Infinity
  for file in tqdm(utils.get_file_names(args.data_path)):
    data_file = os.path.join(args.data_path, file)
    month = file.replace('.jsonl', '')
    print(f"data_file: {data_file}")
    for toxic in args.toxic_label:
      twlen_df_dict[toxic].loc[month] = 0
    twlen_df_dict['all'].loc[month] = 0

    with open(data_file, 'r') as f:
      for line in f:
        tw_json = json.loads(line)
        tw_length = len(tw_json['text'])
        curr_len_label = labeling_tw_len(tw_length)
        if curr_len_label:
          twlen_df_dict['all'].at[month, curr_len_label] += 1
        for toxic in args.toxic_label:
          if curr_len_label and tw_json[toxic] == 1:
            twlen_df_dict[toxic].at[month, curr_len_label] += 1

    twlen_df_dict['all'].at[month, 'all'] = twlen_df_dict['all'].loc[month].sum()
    for toxic in args.toxic_label:
      twlen_df_dict[toxic].at[month, 'all'] = twlen_df_dict[toxic].loc[month].sum()
    print(f"{month} finished!!")

  print(f"all df: {twlen_df_dict['all']}")
  twlen_df_dict['all'].to_csv(f"{args.table_path}all.csv")
  for toxic in args.toxic_label:
    print(f"{toxic} df: {twlen_df_dict[toxic]}")
    twlen_df_dict[toxic].to_csv(f"{args.table_path}{toxic}.csv")

if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
