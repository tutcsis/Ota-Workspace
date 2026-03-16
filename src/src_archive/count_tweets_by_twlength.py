from pathes import (
	TOXIC_TWEET_PATH,
	TWLENGTH_TABLE_PATH,
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
	data_path: str = TOXIC_TWEET_PATH
	table_path: str = TWLENGTH_TABLE_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

def labeling_tw_len(tw_length):
  if tw_length > 140:
    return 'g140'
  return f'le{((tw_length-1)//20+1)*20}'


def main(args):
	twlength_df_dict = dict()
	for toxic in args.toxic_label:
		twlength_df_dict[toxic] = pd.DataFrame(
			columns=['le20', 'le40', 'le60', 'le80', 'le100', 'le120', 'le140', 'g140', 'all']
		)
	print(twlength_df_dict)
	for file in utils.get_file_names(args.data_path):
		data_file = os.path.join(args.data_path, file)
		month = file.replace('.jsonl', '')
		print(f"data_file: {data_file}")
		for toxic in args.toxic_label:
			twlength_df_dict[toxic].loc[month] = 0
		with open(data_file, 'r') as f:
			for line in f:
				tw_json = json.loads(line)
				tw_length = len(tw_json['text'])
				for toxic in args.toxic_label:
					curr_len_label = labeling_tw_len(tw_length)
					if tw_json[toxic] == 1:
						twlength_df_dict[toxic].at[month, curr_len_label] += 1
		for index in twlength_df_dict.keys():
			twlength_df_dict[index].at[month, 'all'] = twlength_df_dict[index].loc[month].sum()
			print(f"{index} finished!!")

	for toxic in args.toxic_label:
		twlength_df_dict[toxic].to_csv(f"{args.table_path}{toxic}.csv")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

