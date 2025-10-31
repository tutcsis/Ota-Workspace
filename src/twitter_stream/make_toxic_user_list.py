import os
import json
import pandas as pd
from tap import Tap
from collections import Counter

class Args(Tap):
	data_path: str = "tables/user_tweet_count/"
	output_path: str = "data/twitter_stream/toxic_user_list.txt"
	toxic_label: str = ["obscene", "discriminatory", "violent"]

def get_files(path: str):
	return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def main(args):
	toxic_users = set()
	for file in get_files(args.data_path):
		file_path = os.path.join(args.data_path, file)
		print(f"Processing file: {file_path}")
		with open(file_path, "r") as f:
			df = pd.read_csv(f)
			for toxic in args.toxic_label:
				users = df[df[toxic] > 0]['toxic_user'].tolist()
				toxic_users.update(users)
	with open(args.output_path, "w") as f:
		for user in toxic_users:
			f.write(f"{user}\n")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
