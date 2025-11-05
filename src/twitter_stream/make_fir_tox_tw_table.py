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

def main(args):
	print(f"input folder path: {args.input_folder}")

	# make output df dict
	with open(args.toxic_users_path, 'r') as f:
		user_ids = [s.rstrip() for s in f.readlines()]
	tw_count_df_dict = dict()
	user_year_df_dict = dict()
	for toxic in args.toxic_label + ['all']:
		tw_count_df_dict[toxic] = pd.DataFrame(0, columns=args.years, index=user_ids, dtype=np.int64)
		user_year_df_dict[toxic] = pd.DataFrame(0, columns=args.years + ["user_year"], index=user_ids, dtype=np.int64)

	# print(f"tw_count_df: {tw_count_df_dict}")
	# print(f"user_year_df: {user_year_df_dict}")

	# read each yearly toxic user table
	for i_file in tqdm(utils.get_file_names(args.input_folder)):
		i_file_path = os.path.join(args.input_folder, i_file)
		month = i_file.split('.csv')[0]
		year = i_file.split('-')[0]
		if year not in args.years:
			continue
		print(f"file name: {i_file}, year: {year}")
		# if not month.split('-')[1] == '01':
		# 	continue
		i_df = pd.read_csv(i_file_path, index_col=0, dtype=int)
		for toxic in args.toxic_label + ['all']:
			curr_values = np.array(tw_count_df_dict[toxic][year])
			new_values = np.array(i_df[toxic])
			tw_count_df_dict[toxic].loc[:, year] = curr_values + new_values
			# print(tw_count_df_dict[toxic])
		# print(f"tw_count_df_dict: {Counter(tw_count_df_dict['obscene'][year])}")
		# print(f"i_df: {Counter(i_df['obscene'])}")
		# print(f"tw_count_df: {tw_count_df_dict['obscene']['2012']}")
		# print(f"i_df: {i_df['obscene']}")
		# return

	# save toxic tweet count table
	for toxic in args.toxic_label + ['all']:
		output_path = os.path.join(args.output1_folder, f"{toxic}.csv")
		tw_count_df_dict[toxic].to_csv(output_path)
		# print(f"Saved toxic tweet count table to {output_path}")
	# print(tw_count_df_dict)
	print(f"toxic: obscene")
	for year in args.years:
		print(f"year: {year}, {Counter(tw_count_df_dict['obscene'][year])}")

	# for toxic in args.toxic_label + ['all']:
	# 	for year in args.years:
	# 		user_year_df_dict[toxic][year] = (year if tw_count_df_dict[toxic][year] > 0 else 9999).astype(int)
	# print(f"user_year_df_dict: {user_year_df_dict}")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

