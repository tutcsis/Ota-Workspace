from pathes import (
	TOXIC_MEDIA_TWEET_PATH,
	TOXIC_MEDIA_TABLE_PATH,
	ALL_MEDIA_TABLE,
	TOXIC_LABEL,
	USE_YEARS,
)
import utils
import os
import json
import numpy as np
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	toxic_media_folder: str = TOXIC_MEDIA_TWEET_PATH
	toxic_media_table: str = TOXIC_MEDIA_TABLE_PATH
	all_media_table: str = ALL_MEDIA_TABLE
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
	print(f"toxic_media_folder: {args.toxic_media_folder}")

	# make output df dict
	months = []
	for year in args.years:
		for month in range(1, 13):
			months.append(f"{year}-{str(month).zfill(2)}")
	media_toxic_df_dict = dict()
	for toxic in args.toxic_label + ['all']:
		media_toxic_df_dict[toxic] = pd.DataFrame(0, columns=args.url_label + ["all"], index=months, dtype=np.int64)

	# set media toxic monthly
	for file in tqdm(utils.get_file_names(args.toxic_media_folder)):
		month = file.split('.jsonl')[0]
		year = month.split('-')[0]
		if year not in args.years:
			continue
		
		with open(os.path.join(args.toxic_media_folder, file), 'r') as f:
			for line in f:
				tw = json.loads(line)
				if args.mode == 'toxic':
					for toxic in args.toxic_label:
						if not tw[toxic]:
							continue
						media_toxic_df_dict[toxic].loc[month, check_media_type(tw)] += 1
						media_toxic_df_dict[toxic].loc[month, "all"] += 1
				elif args.mode == 'all':
					media_toxic_df_dict['all'].loc[month, check_media_type(tw)] += 1
					media_toxic_df_dict['all'].loc[month, "all"] += 1

	# save toxic media tweet count table
	if args.mode == 'toxic':
		for toxic in args.toxic_label:
			print(toxic, media_toxic_df_dict[toxic])
			output_path = os.path.join(args.toxic_media_table, f"{toxic}.csv")
			media_toxic_df_dict[toxic].to_csv(output_path)
	elif args.mode == 'all':
		media_toxic_df_dict['all'].to_csv(args.all_media_table)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
