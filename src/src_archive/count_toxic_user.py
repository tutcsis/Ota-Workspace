import os
import json
import pandas as pd
from tap import Tap
from collections import Counter

class Args(Tap):
	data_path: str = "data/twitter_stream/1000-toxic-sampling-user_add/"
	user_count_table_path: str = "tables/user_tweet_count/"
	output_path: str = "tables/1000_toxic_user_count.csv"
	toxic_label: str = ["obscene", "discriminatory", "violent"]

def get_files(path: str):
	return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def main(args):
	user_counts = {}
	for file in get_files(args.data_path):
		file_path = os.path.join(args.data_path, file)
		print(f"Processing file: {file_path}")
		data_list = {}
		with open(file_path, "r") as f:
			for i, line in enumerate(f):
				data_list[str(i)] = json.loads(line)
		df = pd.DataFrame.from_dict(data_list, orient="index")

		all_user_tweet_df = pd.DataFrame()
		user_count_list = []
		for toxic in args.toxic_label:
			user_list = df[df[toxic] == 1]['user_id'].tolist()
			user_tweet_count = dict(Counter(user_list))
			user_tweet_df = pd.DataFrame.from_dict(user_tweet_count, orient="index", columns=[toxic])
			user_tweet_df = user_tweet_df.reset_index().rename(columns={"index": "toxic_user"})
			all_user_tweet_df = pd.merge(all_user_tweet_df, user_tweet_df, on="toxic_user", how="outer") if not all_user_tweet_df.empty else user_tweet_df
			user_count_list.append(len(set(user_list)))
		all_user_tweet_df = all_user_tweet_df.fillna(0).astype(int)
		print(all_user_tweet_df)
		all_user_tweet_df.to_csv(os.path.join(args.user_count_table_path, file.replace(".jsonl", ".csv")), index=False)
		user_counts[file.replace(".jsonl", "")] = user_count_list
	print(user_counts)
	df_counts = pd.DataFrame.from_dict(user_counts, orient="index", columns=args.toxic_label)
	df_counts = df_counts.sort_index()
	print(df_counts)
	df_counts.to_csv(args.output_path)

		# # 有害な投稿についているuser_idをリストに入れてカウント
		# df['is_toxic'] = df[args.toxic_label].max(axis=1)
		# user_list = df[df['is_toxic'] == 1]['user_id'].tolist()
		# user_tweet_count = dict(Counter(user_list))

		# # ユーザ名と有害投稿数のデータフレームを作成して保存
		# user_tweet_df = pd.DataFrame.from_dict(user_tweet_count, orient="index", columns=["tweet_count"])
		# user_tweet_df = user_tweet_df.reset_index().rename(columns={"index": "toxic_user"})
		# user_tweet_df.to_csv(os.path.join(args.user_count_table_path, file.replace(".jsonl", ".csv")), index=False)

		# # 有害ユーザ数をカウントして辞書に保存
		# user_counts[file.replace(".jsonl", "")] = len(set(user_list))

	# df_counts = pd.DataFrame.from_dict(user_counts, orient="index", columns=["toxic_user_count"])
	# df_counts = df_counts.sort_index()
	# print(df_counts)
	# df_counts.to_csv(args.output_path)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
