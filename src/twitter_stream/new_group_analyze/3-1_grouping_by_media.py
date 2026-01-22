import json
import numpy as np
import os
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import utils
from pathes import (
	TOXIC_LABEL,
	USE_YEARS,
)
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	data_path: str = "data/twitter_stream/sampled-toxic_ja-0_001/"
	table_path: str = "tables/new_group_analyze/3-3_media_group/"
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	url_label: list = ["url", "media", "both", "other"]
	mode: str = "all"

def check_media_type(tw):
	has_url = False
	has_media = False
	if 'urls' in tw and len(tw['urls']) > 0:
		has_url = True
	if 'media' in tw and len(tw['media']) > 0:
		has_media = True

	if has_url and has_media:
		return "both"
	elif has_url:
		return "url"
	elif has_media:
		return "media"
	else:
		return "other"

def main(args):
	print(f"data: {args.data_path}")
	print(f"table: {args.table_path}")

	# make output df dict
	months = []
	for year in args.years:
		for month in range(1, 13):
			months.append(f"{year}-{str(month).zfill(2)}")
	media_toxic_df_dict = dict()
	for toxic in args.toxic_label + ['all']:
		media_toxic_df_dict[toxic] = pd.DataFrame(0, columns=args.url_label + ["all"], index=months, dtype=np.int64)

	# set media toxic monthly
	for file in tqdm(utils.get_file_names(args.data_path)):
		month = file.split('.jsonl')[0]
		year = month.split('-')[0]
		if year not in args.years:
			continue
		
		with open(os.path.join(args.data_path, file), 'r') as f:
			for line in f:
				tw = json.loads(line)
				for toxic in args.toxic_label + ['all']:
					if toxic != 'all' and not tw[toxic]:
						continue
					media_toxic_df_dict[toxic].loc[month, check_media_type(tw)] += 1
					media_toxic_df_dict[toxic].loc[month, "all"] += 1

	# save toxic media tweet count table
	for toxic in args.toxic_label + ['all']:
		output_path = os.path.join(args.table_path, f"{toxic}.csv")
		media_toxic_df_dict[toxic].to_csv(output_path)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
