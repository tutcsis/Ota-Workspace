from pathes import (
	USER_TOXIC_COUNTS_PATH,
	GROUPED_USER_TABLE,
	TOXIC_USER_LIST,
	TOXIC_LABEL,
	USE_YEARS
)
import utils
import os
import json
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	input_table_path: str = USER_TOXIC_COUNTS_PATH
	output_table_file: str = GROUPED_USER_TABLE
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS

def main(args):
	yearly_users_df = dict()
	grouped_users_df = []
	# create df that column is years and index is user_id
	with open(TOXIC_USER_LIST, 'r') as f:
		user_ids = [s.rstrip() for s in f.readlines()]
	for toxic in args.toxic_label + ['all']:
		yearly_users_df[toxic] = pd.DataFrame(columns=args.years + ['group'], index=user_ids, dtype=int)
		yearly_users_df[toxic] = yearly_users_df[toxic].fillna(0)
	print(yearly_users_df)
	# return

	for file in utils.get_file_names(args.input_table_path):
		print(f"Processing file: {file}")
		file_path = os.path.join(args.input_table_path, file)
		year = file.split('-')[0]

		# skip 2011, 2021
		if year not in args.years:
			print(f"Skipping year: {year}")
			continue

		df = pd.read_csv(file_path, index_col=0)
		# add to yearly_users_df
		for toxic in args.toxic_label + ['all']:
			yearly_users_df[toxic][year] = yearly_users_df[toxic][year].add(df[toxic], fill_value = 0)

	# set group column(rule -> README.md)
	for toxic in args.toxic_label + ['all']:
		def set_group(row):
			check = [0, 0, 0]
			if row['2012'] and row['2013'] and row['2014']:
				check[0] = 1
			if row['2015'] and row['2016'] and row['2017']:
				check[1] = 1
			if row['2018'] and row['2019'] and row['2020']:
				check[2] = 1
			if check == [1, 1, 1]:
				return 1
			elif check == [1, 0, 0]:
				return 2
			elif check == [0, 1, 0]:
				return 3
			elif check == [0, 0, 1]:
				return 4
			else:
				return 0
		yearly_users_df[toxic]['group'] = yearly_users_df[toxic][args.years].apply(set_group, axis=1)
		print(f"{toxic}: {Counter(yearly_users_df[toxic]['group'])}")

		# append to grouped_users_df
		# grouped_users_df = grouped_users_df.join(yearly_users_df[toxic]['group'], how='outer', rsuffix=f'g_{toxic}')
		temp_df = yearly_users_df[toxic][['group']].copy()
		temp_df.columns = [f"g_{toxic}"]
		grouped_users_df.append(temp_df)
	grouped_users_df = pd.concat(grouped_users_df, axis=1)
	grouped_users_df = grouped_users_df.fillna(0)
	print(grouped_users_df)
	for column in grouped_users_df.columns:
		print(f"Group counts for {column}: {Counter(grouped_users_df[column])}")

	print(f"yearly toxic users")
	for toxic in args.toxic_label + ['all']:
		for year in args.years:
			print(f"{toxic} - {year}: {Counter(yearly_users_df[toxic][year])}")

	grouped_users_df.to_csv(args.output_table_file)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

