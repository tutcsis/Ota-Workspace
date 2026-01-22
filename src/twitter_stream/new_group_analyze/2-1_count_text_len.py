import japanize_matplotlib
import json
import matplotlib.pyplot as plt
import os
import pandas as pd
import random
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import utils
from pathes import (
	USE_YEARS
)
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	tweet_folder: str = "data/twitter_stream/sampled-toxic_ja-0_001/"
	table_path: str = "tables/new_group_analyze/2-1-1_text_len.csv"
	table2_path: str = "tables/new_group_analyze/2-1-2_text_len_280.csv"
	graph_path: str = "imgs/new_group_analyze/2-1-1_text_len.png"
	graph2_path: str = "imgs/new_group_analyze/2-1-2_text_len_280.png"
	years: list = USE_YEARS	

	max_twlen: int = 140

	graph_title: str = "ツイートの文字数の分布"
	graph_xlabel: str = "文字数"
	graph_ylabel: str = "出現回数"

def make_tw_counts_table(args, max_twlen=None, table_path=None):
	tw_len_df = pd.DataFrame(columns=['count'], index=range(1, (max_twlen+1)+1), dtype=int)
	tw_len_df = tw_len_df.fillna(0)

	print(f"tweet folder: {args.tweet_folder}")
	for tw_file in tqdm(utils.get_file_names(args.tweet_folder)):
		year = tw_file.split('-')[0]
		if year not in args.years:
			continue
		tw_path = os.path.join(args.tweet_folder, tw_file)
		with open(tw_path, 'r') as f:
			for line in f:
				data = json.loads(line)
				tw_len = min(len(data['text']), max_twlen + 1)
				tw_len_df.loc[tw_len, 'count'] += 1

	# save csv
	tw_len_df.to_csv(table_path)
	print(f"Saved to {table_path}")

def make_graph(args, tw_len_df, graph_path, grid_dis=10, max_twlen=None):
	plt.figure()
	plt.plot(tw_len_df.index, tw_len_df['count'], label='tweet count', marker='o')
	plt.xticks(
		range(0, (max_twlen + 1)+1, grid_dis),
		range(0, (max_twlen + 1)+1, grid_dis)
	)
	plt.title(args.graph_title)
	plt.xlabel(args.graph_xlabel)
	plt.ylabel(args.graph_ylabel)
	plt.legend()
	plt.grid(True)
	plt.tight_layout()
	plt.savefig(graph_path)
	print(f"Saved to {graph_path}")

def main(args):
	# make tw len counts table
	if not os.path.exists(args.table_path):
		make_tw_counts_table(args, args.max_twlen, args.table_path)
	if not os.path.exists(args.table2_path):
		make_tw_counts_table(args, args.max_twlen*2, args.table2_path)

	# load tw len counts table
	tw_len_df = pd.read_csv(args.table_path, index_col=0, dtype=int)
	tw_len2_df = pd.read_csv(args.table2_path, index_col=0, dtype=int)

	# make graph
	make_graph(args, tw_len_df, args.graph_path, grid_dis=10, max_twlen=args.max_twlen)
	make_graph(args, tw_len2_df, args.graph2_path, grid_dis=20, max_twlen=args.max_twlen*2)

if __name__ == '__main__':
	args = Args().parse_args()
	main(args)
