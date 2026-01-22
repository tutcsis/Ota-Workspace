import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import utils
from pathes import (
	USE_YEARS,
  TOXIC_LABEL
)
from tap import Tap

class Args(Tap):
	table_path: str = "tables/new_group_analyze/0-4_toxic_count.csv"
	graph_path: str = "imgs/new_group_analyze/0-4_toxic_count.png"

	user_years: list = USE_YEARS
	graph_labels: list = TOXIC_LABEL
	graph_title: str = "有害投稿数"
	graph_xlabel: str = "投稿した年月"
	graph_ylabel: str = "有害投稿の割合"
	toxic_limit: int = 10

def make_tweet_graph(args, df):
	# スパム投稿を除外
  for toxic in args.graph_labels:
    # 欠損値は 0 で割らないようにする
    df.loc[df['total'] != 0, toxic] = df[toxic] / df['total'] * 100
    df[toxic] = df[toxic].apply(lambda x: x if x <= args.toxic_limit else args.toxic_limit)
  print(df.head()[args.graph_labels + ['total']])

  print("Plotting rate graph[%]")
  plt.figure()
  for toxic in args.graph_labels:
    plt.plot(df.index, df[toxic], label=toxic, marker='o')
  plt.xticks(
    range(0, 12*len(args.user_years)+1, 12),
    args.user_years + [""]
  )

  plt.grid(True)
  plt.legend()
  plt.title(f"{args.graph_title}")
  plt.xlabel(args.graph_xlabel)
  plt.ylabel(f"{args.graph_ylabel}[%]")
  plt.tight_layout()
  plt.savefig(args.graph_path)
  plt.close()

def main(args):
	df = pd.read_csv(args.table_path)
	df.set_index('month', inplace=True)
	df = df[df.index.str.split('-').str[0].isin(args.user_years)]
	# 欠損月を0埋め
	for year in args.user_years:
		for month in range(1, 12+1):
			id = f"{year}-{str(month).zfill(2)}"
			if id not in df.index:
				df.loc[id] = [0 for _ in range(len(df.columns))]
				print('Added month: ', id)
	df = df.sort_index()

	make_tweet_graph(args, df)


if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

