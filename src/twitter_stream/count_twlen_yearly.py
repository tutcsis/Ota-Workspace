from pathes import (
  ALL_JA_TW_TEXT_PATH,
  TWLEN_COUNT_TABLE_PATH,
  TOXIC_LABEL,
	USE_YEARS,
	GROUP
)
import utils
import os
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
  all_ja_tw_text_folder: str = ALL_JA_TW_TEXT_PATH
  all_twlen_table_folder: str = TWLEN_COUNT_TABLE_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

def main(args):
  print(f"tw_text folder: {args.all_ja_tw_text_folder}")
  for month in utils.get_folder_names(args.all_ja_tw_text_folder):
    print(f"Processing month: {month}")
    month_path = os.path.join(args.all_ja_tw_text_folder, month)
    for tw_file in tqdm(utils.get_file_names(month_path)):
      tw_file_path = os.path.join(month_path, tw_file)
      with open(tw_file_path, "r") as f:
        text_dict = json.load(f)
        print(text_dict)
      return

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
