from pathes import (
	TOXIC_USERS_PATH,
	YEARLY_TOXIC_USER_TABLE,
	G_USERS_TABLE_PATH,
	TOXIC_TW_COUNT_PATH,
	TOXIC_LABEL,
	USE_YEARS,
	GROUP
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
	input_folder: str = YEARLY_TOXIC_USER_TABLE
	output1_folder: str = TOXIC_TW_COUNT_PATH
	output2_folder: str = G_USERS_TABLE_PATH
	toxic_users_path: str = TOXIC_USERS_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

def make_user_year_table(args, tw_count_df_dict):
	# read each yearly toxic user table
	for i_file in tqdm(utils.get_file_names(args.input_folder)):
		i_file_path = os.path.join(args.input_folder, i_file)
		month = i_file.split('.csv')[0]
		year = i_file.split('-')[0]
		if year not in args.years:
			continue
		print(f"file name: {i_file}, year: {year}")
		i_df = pd.read_csv(i_file_path, index_col=0, dtype=int)
		for toxic in args.toxic_label + ['all']:
			curr_values = np.array(tw_count_df_dict[toxic][year])
			new_values = np.array(i_df[toxic])
			tw_count_df_dict[toxic].loc[:, year] = curr_values + new_values

	# save toxic tweet count table
	for toxic in args.toxic_label + ['all']:
		output_path = os.path.join(args.output1_folder, f"{toxic}.csv")
		tw_count_df_dict[toxic].to_csv(output_path)
	# print(tw_count_df_dict)
	print(f"toxic: obscene")
	for year in args.years:
		print(f"year: {year}, {Counter(tw_count_df_dict['obscene'][year])}")


def main(args):
	print(f"input folder path: {args.input_folder}")

	# make output df dict
	with open(args.toxic_users_path, 'r') as f:
		user_ids = [s.rstrip() for s in f.readlines()]
	tw_count_df_dict = dict()
	user_year_df_dict = dict()
	group_user_df_dict = dict()
	for toxic in args.toxic_label + ['all']:
		tw_count_df_dict[toxic] = pd.DataFrame(0, columns=args.years, index=user_ids, dtype=np.int64)
		user_year_df_dict[toxic] = pd.DataFrame(0, columns=args.years + ["user_year"], index=user_ids, dtype=np.int64)
		group_user_df_dict[toxic] = pd.DataFrame(0, columns=args.years, index=user_ids, dtype=np.int64)

	# make toxic tweet count table
	if not os.path.exists(os.path.join(args.output1_folder, 'obscene.csv')):
		print("not exist")
		make_user_year_table(args, tw_count_df_dict)
	else:
		print("exist")
		for toxic in args.toxic_label + ['all']:
			tw_count_df_dict[toxic] = pd.read_csv(os.path.join(args.output1_folder, f"{toxic}.csv"), index_col=0, dtype=np.int64)
		# print(tw_count_df_dict)

	# set toxic tweet year table	
	for toxic in args.toxic_label + ['all']:
		for year in args.years:
			curr_values = np.array(tw_count_df_dict[toxic][year])
			user_year_df_dict[toxic][year] = np.array([int(year) if count > 0 else 9999 for count in curr_values])
		user_year_df_dict[toxic]['user_year'] = user_year_df_dict[toxic][args.years].min(axis=1)
		print(f"toxic: {toxic}, {Counter(user_year_df_dict[toxic]['user_year'])}")

		# make group user table
		def set_group(value, year):
			group_val = year - value
			if group_val < 0:
				return -1
			elif group_val >= 4:
				return 4
			else:
				return group_val

		for year in args.years:
			curr_values = np.array(user_year_df_dict[toxic]['user_year'])
			group_user_df_dict[toxic][year] = np.array([set_group(int(val), int(year)) for val in curr_values])
		# save group user table
		group_user_df_dict[toxic].to_csv(os.path.join(args.output2_folder, f"{toxic}.csv"))
		print(f"saved {toxic} group user table!!!")

	# print(f"user_year_df_dict: {user_year_df_dict}")
	# print(f"group_user_df_dict: {group_user_df_dict}")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

