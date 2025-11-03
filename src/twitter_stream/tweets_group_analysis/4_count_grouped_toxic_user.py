from pathes import (
	GROUPED_TOXIC_COUNTS_PATH,
	GROUPED_MONTHLY_COUNTS_PATH,
	TOXIC_LABEL,
	USE_YEARS,
	GROUP
)
import utils
import os
import json
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	input_path: str = GROUPED_TOXIC_COUNTS_PATH
	output_path: str = GROUPED_MONTHLY_COUNTS_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

def main(args):
	output_str = dict()
	for toxic in args.toxic_label + ['all']:
		output_str[toxic] = f",{','.join(map(str, args.groups))},all\n"

	for file in utils.get_file_names(args.input_path):
		input_file = os.path.join(args.input_path, file)
		month = file.replace('.csv', '')
		print(f"input_path: {args.input_path}")
		for toxic in args.toxic_label + ['all']:
			df = pd.read_csv(input_file, index_col=0)

			counts_str = f"{month},"
			all_count = 0
			for group in args.groups:
				# print(f'toxic: {toxic}, group: {group}, {Counter(df[df[f"g_{toxic}"] == group][toxic])}')
				curr_count = df[df[f"g_{toxic}"] == group][toxic].sum()
				all_count += curr_count
				counts_str += f"{curr_count},"
			counts_str += str(all_count)
			# print(counts_str)
			output_str[toxic] += counts_str + "\n"
		print(f"Finished processing month: {month}")

	for toxic in args.toxic_label + ['all']:
		output_file = os.path.join(args.output_path, f"{toxic}.csv")
		with open(output_file, 'w') as f:
			f.write(output_str[toxic])
	print("All done!")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

