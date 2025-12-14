from pathes import (
  SAMPLED_ALL_JA_TW_TEXT_PATH,
  ALL_TWLEN_TABLE_PATH,
  ALL_TWLEN_GRAPH_PATH,
	USE_YEARS
)
import utils
import os
import json
import matplotlib.pyplot as plt
import japanize_matplotlib
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	tweet_folder: str = SAMPLED_ALL_JA_TW_TEXT_PATH
	all_tw_counts_path: str = ALL_TWLEN_TABLE_PATH
	graph_path: str = ALL_TWLEN_GRAPH_PATH
	years: list = USE_YEARS	

	graph_title: str = "ツイートの文字数の分布"
	graph_xlabel: str = "文字数"
	graph_ylabel: str = "出現回数"
	

def make_tw_counts_table(args):
	# init df
	tw_len_df = pd.DataFrame(columns=['count'], index=range(1, 141+1), dtype=int)
	tw_len_df = tw_len_df.fillna(0)
	print(tw_len_df)

	print(f"parent folder: {args.tweet_folder}")
	for tw_file in tqdm(utils.get_file_names(args.tweet_folder)):
		year = tw_file.split('-')[0]
		if year not in args.years:
			continue
		print(f"data file name: {tw_file}")
		tw_path = os.path.join(args.tweet_folder, tw_file)
		for line in open(tw_path, 'r'):
			data = json.loads(line)
			tw_len = len(data['text'])
			if tw_len > 140:
				tw_len = 141
			tw_len_df.loc[tw_len, 'count'] += 1
		print(f"{tw_file} finished!!")
	print(tw_len_df)

	# save csv
	tw_len_df.to_csv(args.all_tw_counts_path)
	print(f"Saved to {args.all_tw_counts_path}")


def main(args):
	# make tw len counts table
	if not os.path.exists(args.all_tw_counts_path):
		make_tw_counts_table(args)
	# load tw len counts table
	tw_len_df = pd.read_csv(args.all_tw_counts_path, index_col=0, dtype=int)
	print(tw_len_df)

	# make graph
	plt.figure()
	plt.plot(tw_len_df.index, tw_len_df['count'], label='tweet count', marker='o')
	plt.xticks(
		range(0, 141+1, 10),
		range(0, 141+1, 10)
	)
	# plt.title(args.graph_title)
	# plt.xlabel(args.graph_xlabel)
	# plt.ylabel(args.graph_ylabel)
	# plt.legend()
	plt.grid(True)
	plt.tight_layout()
	plt.savefig(args.graph_path)

if __name__ == '__main__':
	args = Args().parse_args()
	main(args)
