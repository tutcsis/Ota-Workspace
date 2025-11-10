from pathes import (
	SAMPLED_TWEET_PATH,
	SAMPLED_USERS_PATH,
	SAMPLED_ALL_TWLEN_TABLE_PATH,
	ALL_JA_TW_TEXT_PATH,
	SAMPLED_G_TWLEN_TABLE_PATH,
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
	sampled_tweets_folder: str = SAMPLED_TWEET_PATH
	sampled_user_names: str = SAMPLED_USERS_PATH
	sampled_user_twlen_table: str = SAMPLED_ALL_TWLEN_TABLE_PATH
	sampled_g_twlen_yearly: str = SAMPLED_G_TWLEN_TABLE_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

def make_user_name_list(args):
	user_names = set()
	for file in tqdm(utils.get_file_names(args.sampled_tweets_folder)):
		print(f"file: {file}")
		file_path = os.path.join(args.sampled_tweets_folder, file)
		with open(file_path, "r") as f:
			for line in f:
				tw_json = json.loads(line)
				user_names.add(tw_json['user_id'])
	print(f"Total sampled users: {len(user_names)}")
	# save sampled user names
	with open(args.sampled_user_names, "w") as f:
		for user_name in user_names:
			f.write(f"{user_name}\n")
	return user_names

def make_twlen_yearly_table(args, user_name):
	tw_len_df_dict = dict()
	months = []
	for year in args.years:
		for month in range(1, 13):
			months.append(f"{year}-{str(month).zfill(2)}")
	for year in args.years:
		tw_len_df_dict[year] = pd.DataFrame(0, columns=months, index=list(user_name), dtype=np.int32)

	for file in tqdm(utils.get_file_names(args.sampled_tweets_folder)):
		month = file.split('.jsonl')[0]
		year = month.split('-')[0]
		if year not in args.years:
			continue
		print(f"data file name: {file}")
		tw_path = os.path.join(args.sampled_tweets_folder, file)
		for line in open(tw_path, 'r'):
			data = json.loads(line)
			tw_len_df_dict[year].at[str(data['user_id']), month] += 1

	tw_len_yearly_df = pd.DataFrame(0, columns=args.years, index=list(user_name), dtype=np.int32)
	for year in args.years:
		tw_len_yearly_df.loc[:, year] = np.array(tw_len_df_dict[year].sum(axis=1))
	print(tw_len_yearly_df.head())
	print('2012: ', Counter(tw_len_yearly_df['2012']))
	# save csv
	tw_len_yearly_df.to_csv(args.sampled_user_twlen_table)
	print(f"Saved to {args.sampled_user_twlen_table}")
	return tw_len_yearly_df

def main(args):
	print(f"sampled_tweets folder: {args.sampled_tweets_folder}")
	if not os.path.exists(args.sampled_user_names):
		user_name = make_user_name_list(args)
	else:
		user_name = set()
		with open(args.sampled_user_names, "r") as f:
			for line in f:
				user_name.add(line.strip())
		print(f"Loaded sampled user names from {args.sampled_user_names}, total: {len(user_name)}")

	# make tw len counts table yearly
	if not os.path.exists(args.sampled_user_twlen_table):
		tw_len_yearly_df = make_twlen_yearly_table(args, user_name)
	else:
		tw_len_yearly_df = pd.read_csv(args.sampled_user_twlen_table, index_col=0, dtype=np.int32)
		print(f"Loaded tw len yearly table from {args.sampled_user_twlen_table}")
		print(tw_len_yearly_df.head())

	user_year_df = pd.DataFrame(0, columns=args.years + ["user_year"], index=list(user_name), dtype=np.int32)
	for year in args.years:
		user_year_df[year] = np.array(
			[int(year) if count > 0 else 9999 for count in np.array(tw_len_yearly_df[year])]
		)
	user_year_df['user_year'] = user_year_df[args.years].min(axis=1)

	# make group user table
	group_user_df = pd.DataFrame(0, columns=args.years, index=list(user_name), dtype=np.int32)
	def set_group(value, year):
		group_val = year - value
		if group_val < 0:
			return -1
		elif group_val >= 4:
			return 4
		else:
			return group_val

	for year in args.years:
		group_user_df.loc[:,year] = np.array(
			[set_group(int(val), int(year)) for val in np.array(user_year_df['user_year'])]
		)
	print(f"group_user_df:\n{group_user_df}")

	g_twlen_yearly_df = pd.DataFrame(0, columns=args.groups, index=args.years, dtype=np.int32)
	for year in args.years:
		year_counts = Counter(group_user_df[year])
		for group in args.groups:
			g_twlen_yearly_df.at[year, group] = year_counts[int(group)]
	print(f"g_twlen_yearly_df:\n{g_twlen_yearly_df}")

	# save group user table
	g_twlen_yearly_df.to_csv(args.sampled_g_twlen_yearly)


if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
