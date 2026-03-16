from pathes import (
	G_USERS_TABLE_PATH,
	YEARLY_TOXIC_USER_TABLE,
	G_TWLEN_TABLE_PATH,
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
	user_twlen_table_folder: str = TOXIC_TW_COUNT_PATH
	g_twlen_table_folder: str = G_TWLEN_TABLE_PATH
	toxic_users_file: str = TOXIC_USERS_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

def main(args):
	print(f"g_yearly_table_folder: {args.g_yearly_table_folder}")
	
	with open(args.toxic_users_file, 'r') as f:
		user_ids = [s.rstrip() for s in f.readlines()]
	# make output df dict
	g_user_df_dict = dict()
	user_twlen_df_dict = dict()
	g_tw_count_df_dict = dict()
	for toxic in args.toxic_label + ["all"]:
		g_user_df_dict[toxic] = pd.read_csv(os.path.join(args.g_yearly_table_folder, f"{toxic}.csv"), index_col=0, dtype=str)
		user_twlen_df_dict[toxic] = pd.read_csv(os.path.join(args.user_twlen_table_folder, f"{toxic}.csv"), index_col=0, dtype=np.int64)
		g_tw_count_df_dict[toxic] = pd.DataFrame(0, columns=args.groups, index=args.years, dtype=np.int64)
	
	# set group twlen yearly
	for toxic in args.toxic_label + ["all"]:
		for year in args.years:
			g_tw_count_list = list(g_user_df_dict[toxic][year])
			user_tw_len_list = list(user_twlen_df_dict[toxic][year])
			g_counts = [0]*len(args.groups)
			for i, group in enumerate(g_tw_count_list):
				if group == -1:
					continue
				g_counts[int(group)] += int(user_tw_len_list[i])
			# print(f"g_tw: {Counter(g_tw_count_list)}")
			# print(f"user_twlen: {Counter(user_tw_len_list)}")
			g_tw_count_df_dict[toxic].loc[year] = g_counts
		g_tw_count_df_dict[toxic]['all'] = g_tw_count_df_dict[toxic].sum(axis=1)
		print(f"toxic: {toxic}, g_tw_count_df:\n{g_tw_count_df_dict[toxic]}")
		# save group toxic tweet length table
		output_path = os.path.join(args.g_twlen_table_folder, f"{toxic}.csv")
		g_tw_count_df_dict[toxic].to_csv(output_path)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
