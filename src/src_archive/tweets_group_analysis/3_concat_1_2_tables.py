from pathes import USER_TOXIC_COUNTS_PATH, GROUPED_USER_TABLE, GROUPED_TOXIC_COUNTS_PATH, TOXIC_LABEL, USE_YEARS
import utils
import os
import json
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	group_path: str = GROUPED_USER_TABLE
	user_table_path: str = USER_TOXIC_COUNTS_PATH
	grouped_user_table_path: str = GROUPED_TOXIC_COUNTS_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS

def main(args):
	grouped_users_df = pd.read_csv(args.group_path, index_col=0)
	
	for file in utils.get_file_names(args.user_table_path):
		print(f"Processing file: {file}")
		file_path = os.path.join(args.user_table_path, file)
		year = file.split('-')[0]

		# skip 2011, 2021
		if year not in args.years:
			print(f"Skipping year: {year}")
			continue

		df = pd.read_csv(file_path, index_col=0)

		# merge grouped_users_df and df on index (user_id)
		merged_df = df.join(grouped_users_df, how='left')

		# output df to csv
		output_file_path = os.path.join(args.grouped_user_table_path, file)
		merged_df.to_csv(output_file_path)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

