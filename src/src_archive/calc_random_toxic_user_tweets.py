import random
import os
import json
import pandas as pd
from tap import Tap
from collections import Counter

class Args(Tap):
	user_path: str = "data/twitter_stream/toxic_user_list.txt"
	user_count_table_path: str = "tables/user_tweet_count/"
	# output_path: str = "tables/1000_toxic_user_count.csv"
	toxic_label: str = ["obscene", "discriminatory", "violent"]
	sample_user_len: int = 50
	user_years: list = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]


def get_files(path: str):
	return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def main(args):
	# ランダムにユーザを抽出
	random_users = list()
	user_count = len(open(args.user_path).readlines())
	print(user_count)
	sample_keys = random.sample(range(user_count), args.sample_user_len)
	# print(sample_keys)
	with open(args.user_path, "r") as f:
		for i, line in enumerate(f):
			if i in sample_keys:
				random_users.append(line.strip())
	# print('sampled users: ', random_users)

	user_df = dict()
	for user in random_users:
		user_df[user] = pd.DataFrame(columns=args.toxic_label)
	# print(user_df)

	curr_user = "3310171"
	for file in sorted(get_files(args.user_count_table_path)):
		if not any(year in file for year in args.user_years):
			continue
		print(file)
		file_path = os.path.join(args.user_count_table_path, file)
		# print(f"Processing file: {file_path}")
		df = pd.read_csv(file_path)
		# print(df.head())
		user_data = df[df['toxic_user'] == curr_user]
		if user_data.items():
			print(user_data)
			# user_df[curr_user].loc[file.replace(".csv", "")] = user_data.iloc[0][args.toxic_label]
	# print(curr_user, user_df[curr_user])

	# 各月の有害ユーザの投稿数を集計
	# curr_user = random_users[0]
	

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
