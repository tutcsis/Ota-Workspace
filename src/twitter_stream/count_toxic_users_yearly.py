from pathes import (
	TOXIC_TWEET_PATH,
	TOXIC_USERS_PATH,
	YEARLY_TOXIC_USER_TABLE,
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
	file_path: str = TOXIC_TWEET_PATH
	# file_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/1000-toxic-sampling-user_add/2019-02.jsonl"
	table_path: str = YEARLY_TOXIC_USER_TABLE
	toxic_users_path: str = TOXIC_USERS_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS

def main(args):
	for file in utils.get_file_names(args.file_path):
		print(f"data file name: {file}")
		file_name = os.path.join(args.file_path, file)

		# create df that column is toxic and index is user_id
		with open(args.toxic_users_path, 'r') as f:
			user_ids = [s.rstrip() for s in f.readlines()]
		user_df = pd.DataFrame(columns=args.toxic_label + ['all'], index=user_ids, dtype=int)
		user_df = user_df.fillna(0)
		print(user_df)
		
		print(f"Processing file: {args.file_path}")
		with open(file_name, "r") as f:
			for i, line in enumerate(f):
				# update toxic_count for each user_id
				data = json.loads(line)
				toxic_count = [data[label] for label in args.toxic_label]
				toxic_count.append(sum(toxic_count))
				# check if user is toxic user
				if not toxic_count[-1]:
					continue
				user_df.loc[str(data['user_id'])] += toxic_count
				if i % 1000 == 0:
					print(f"Processed {i} lines")
		for column in user_df.columns:
			print(f"{column}: ", Counter(user_df[column]))
		# save user_df to csv
		output_path = os.path.join(args.table_path, file.replace('.jsonl', '.csv'))
		user_df.to_csv(output_path)
		print(f"Saved to {output_path}")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

## 1 file(10000 lines) counter result
# all:  Counter({0: 9265, 1: 444, 2: 66, 3: 4})
# obscene:  Counter({0: 9482, 1: 295, 2: 2})
# discriminatory:  Counter({0: 9702, 1: 77})
# violent:  Counter({0: 9568, 1: 210, 2: 1})

