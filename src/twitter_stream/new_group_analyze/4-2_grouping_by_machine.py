import os
import json
import numpy as np
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import utils
from pathes import (
  TOXIC_LABEL,
  USE_YEARS
)
from tqdm import tqdm
from tap import Tap

class Args(Tap):
  toxic_jsonl: str = "data/twitter_stream/sampled-toxic_ja-0_001/"
  toxic_table: str = "tables/new_group_analyze/4-2_machine_group/"
  toxic_label: list = TOXIC_LABEL
  years: list = USE_YEARS
  machine_list: list = ["iphone", "ipad", "android", "androidtablet", "web", "other"]

def countup_df(df_dict, month, machine, toxic):
  df_dict[toxic].at[month, machine] += 1
  df_dict[toxic].at[month, 'all'] += 1

def main(args):
  print(f"toxic_jsonl: {args.toxic_jsonl}")

  # make output df dict
  months = []
  for year in args.years:
    for month in range(1, 13):
      months.append(f"{year}-{str(month).zfill(2)}")
  machine_toxic_df_dict = dict()
  for toxic in args.toxic_label + ['all']:
    machine_toxic_df_dict[toxic] = pd.DataFrame(0, columns=args.machine_list + ["all"], index=months, dtype=np.int64)

  # set machine toxic monthly
  for file in tqdm(utils.get_file_names(args.toxic_jsonl)):
    month = file.split('.jsonl')[0]
    year = month.split('-')[0]
    if year not in args.years:
      continue
    with open(os.path.join(args.toxic_jsonl, file), 'r') as f:
      for line in f:
        tw = json.loads(line)
        machine_label = tw['machine_label']
        if machine_label not in args.machine_list:
          machine = "other"

        # all
        countup_df(machine_toxic_df_dict, month, machine_label, 'all')
        # machine_toxic_df_dict['all'].at[month, machine_label] += 1
        # machine_toxic_df_dict['all'].at[month, 'all'] += 1

        # toxic label
        for toxic in args.toxic_label:
          if not tw[toxic]:
            continue
          countup_df(machine_toxic_df_dict, month, machine_label, toxic)
          # machine_toxic_df_dict[toxic].at[month, machine_label] += 1
          # machine_toxic_df_dict[toxic].at[month, 'all'] += 1

  # output table
  print(f"toxic_table: {args.toxic_table}")
  for toxic in args.toxic_label + ['all']:
    output_path = os.path.join(args.toxic_table, f"{toxic}.csv")
    machine_toxic_df_dict[toxic].to_csv(output_path)

if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
