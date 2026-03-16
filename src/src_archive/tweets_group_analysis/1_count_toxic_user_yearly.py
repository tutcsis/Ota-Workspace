from pathes import TOXIC_TWEET_PATH, USER_TOXIC_COUNTS_PATH,TOXIC_LABEL, USE_YEARS
import utils
import os
import json
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	file_path: str = ""
	table_path: str = ""
	# input_path: str = TOXIC_TWEET_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS

def main(args):
	# for file_name in utils.get_file_names(args.input_path):
	# file_path = os.path.join(args.input_path, file_name)
	# create df that column is [obscene, discriminatory, violent, all] and index is user_id
	user_df = pd.DataFrame(columns=args.toxic_label + ['all'])
	# user_df.loc['111'] = [1, 1, 1, 3]
	# user_df.loc['222'] = [2, 2, 2, 6]
	# print('before', user_df)
	# if '111' in user_df.index:
	# 	user_df.loc['111'] += [1, 1, 1, 3]
	# print('after', user_df)
	# return
	
	print(f"Processing file: {args.file_path}")
	with open(args.file_path, "r") as f:
		for i, line in enumerate(f):
			# update toxic_count for each user_id
			data = json.loads(line)
			user_id = data['user_id']
			toxic_count = [data[label] for label in args.toxic_label]
			toxic_count.append(sum(toxic_count))
			if user_id in user_df.index:
				user_df.loc[user_id] += toxic_count
			else:
				user_df.loc[user_id] = toxic_count
			if i % 1000 == 0:
				print(f"Processed {i} lines")
	# print(user_df)
	# save user_df to csv
	# table_path = os.path.join(USER_TOXIC_COUNTS_PATH, file_name.replace('.jsonl', '.csv'))
	user_df.to_csv(args.table_path)
	print(f"Saved to {args.table_path}")
	# return

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

## 1 file(10000 lines) counter result
# all:  Counter({0: 9265, 1: 444, 2: 66, 3: 4})
# obscene:  Counter({0: 9482, 1: 295, 2: 2})
# discriminatory:  Counter({0: 9702, 1: 77})
# violent:  Counter({0: 9568, 1: 210, 2: 1})

