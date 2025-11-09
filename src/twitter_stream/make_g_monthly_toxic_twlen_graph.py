from pathes import (
	G_USERS_TABLE_PATH,
	YEARLY_TOXIC_USER_TABLE,
	G_TWLEN_MONTHLY_TABLE_PATH,
	TOXIC_USERS_PATH,
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
	g_yearly_table_folder: str = G_USERS_TABLE_PATH
	user_twlen_table_folder: str = YEARLY_TOXIC_USER_TABLE
	g_twlen_table_folder: str = G_TWLEN_MONTHLY_TABLE_PATH
	toxic_users_file: str = TOXIC_USERS_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

def main(args):
	print(f"g_yearly_table_folder: {args.g_yearly_table_folder}")
	print(f"user_twlen_table_folder: {args.user_twlen_table_folder}")
	
	with open(args.toxic_users_file, 'r') as f:
		user_ids = [s.rstrip() for s in f.readlines()]
	# make output df dict
	g_user_df_dict = dict()
	g_tw_count_df_dict = dict()
	months = []
	for year in args.years:
		for month in range(1, 13):
			months.append(f"{year}-{str(month).zfill(2)}")
	for toxic in args.toxic_label + ["all"]:
		g_user_df_dict[toxic] = pd.read_csv(os.path.join(args.g_yearly_table_folder, f"{toxic}.csv"), index_col=0, dtype=str)
		g_tw_count_df_dict[toxic] = pd.DataFrame(0, columns=args.groups, index=months, dtype=np.int64)
	
	# set group twlen yearly
	for file in utils.get_file_names(args.user_twlen_table_folder):
		file_path = os.path.join(args.user_twlen_table_folder, file)
		month = file.split('.csv')[0]
		year = file.split('-')[0]
		if year not in args.years:
			continue
		tw_count_df = pd.read_csv(file_path, index_col=0, dtype=np.int64)
		g_counts = [0]*len(args.groups)
		for toxic in args.toxic_label + ["all"]:
			g_tw_count_list = list(g_user_df_dict[toxic][year])
			user_tw_len_list = list(tw_count_df[toxic])
			for i, group in enumerate(g_tw_count_list):
				if group == -1:
					continue
				g_counts[int(group)] += int(user_tw_len_list[i])
			g_tw_count_df_dict[toxic].loc[month] = g_counts
	
	for toxic in args.toxic_label + ["all"]:
		print(toxic, g_tw_count_df_dict[toxic])
		# save group toxic tweet length table
		output_path = os.path.join(args.g_twlen_table_folder, f"{toxic}.csv")
		g_tw_count_df_dict[toxic].to_csv(output_path)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
