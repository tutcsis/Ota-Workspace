import os
import json
import matplotlib.pyplot as plt
import numpy as np
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
	input_path: str = "data/twitter_stream/sampled-toxic_ja-0_001/"
	user_list: str = "tables/new_group_analyze/1-1_user_fast_month.json"
	table_path: str = "tables/new_group_analyze/1-1_usage_group/"
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: str = ["0", "1", "2", "3", "4"]
	max_year = 4

def make_user_list(args):
	print("make user list")
	users = dict()
	for file in tqdm(utils.get_file_names(args.input_path)):
		month = file.split('.jsonl')[0]
		year = month.split('-')[0]
		if year not in args.years:
			continue

		file_path = os.path.join(args.input_path, file)
		with open(file_path, 'r', encoding='utf-8') as f:
			for line in f:
				json_data = json.loads(line.strip())
				user_id = json_data.get("user_id", "")
				if user_id not in users:
					users[user_id] = month

	with open(args.user_list, "w", encoding="utf-8") as f:
		json.dump(users, f, indent=4, ensure_ascii=False)

def calc_tweet_year(args, first_month, curr_month):
	first_year = int(first_month.split('-')[0])
	curr_year = int(curr_month.split('-')[0])
	first_month = int(first_month.split('-')[1])
	curr_month = int(curr_month.split('-')[1])
	tw_year = float((curr_year - first_year)*12 + (curr_month - first_month))/12.0
	year_label = min(int(tw_year), args.max_year)
	return int(year_label)

def make_user_year_table(args):
	# make output df dict
	months = []
	for year in args.years:
		for month in range(1, 13):
			months.append(f"{year}-{str(month).zfill(2)}")
	tw_year_toxic_df_dict = dict()
	for toxic in args.toxic_label + ['all']:
		tw_year_toxic_df_dict[toxic] = pd.DataFrame(0, columns=args.groups + ["all"], index=months, dtype=np.int64)

	# load user list
	with open(args.user_list, "r", encoding="utf-8") as f:
		users = json.load(f)

	for file in tqdm(utils.get_file_names(args.input_path)):
		group_count_dict = dict()
		for toxic in args.toxic_label + ['all']:
			group_count_dict[toxic] = [0]*(args.max_year+1)

		month = file.split('.jsonl')[0]
		year = month.split('-')[0]
		if year not in args.years:
			continue

		file_path = os.path.join(args.input_path, file)
		with open(file_path, 'r', encoding='utf-8') as f:
			for line in f:
				json_data = json.loads(line.strip())
				user_id = str(json_data.get("user_id", ""))
				if user_id in users.keys():
					first_month = users[user_id]
					year_label = calc_tweet_year(args, first_month, month)
					for toxic in args.toxic_label:
						if json_data.get(toxic, 0):
							group_count_dict[toxic][year_label] += 1
					group_count_dict['all'][year_label] += 1
				else:
					print(f"Error: user_id {user_id} not in users")

		for i in args.groups:
			for toxic in args.toxic_label + ['all']:
				tw_year_toxic_df_dict[toxic].loc[month, str(i)] = group_count_dict[toxic][int(i)]
				tw_year_toxic_df_dict[toxic].loc[month, "all"] += group_count_dict[toxic][int(i)]

	# save toxic tweet count table
	for toxic in args.toxic_label + ['all']:
		output_path = os.path.join(args.table_path, f"{toxic}.csv")
		tw_year_toxic_df_dict[toxic].to_csv(output_path)
	print("saved user year table")

def main(args):
	print(f"input_path: {args.input_path}")
	if not os.path.exists(args.user_list):
		make_user_list(args)

	make_user_year_table(args)


if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
