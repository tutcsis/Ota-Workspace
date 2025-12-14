from pathes import (
	G_TWLEN_MONTHLY_TABLE_PATH,
	G_YEARLY_TWLEN_GRAPH_PATH,
	TOXIC_LABEL,
	USE_YEARS,
	GROUP
)
import utils
import os
import json
import matplotlib.pyplot as plt
import japanize_matplotlib
import numpy as np
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	table_path: str = G_TWLEN_MONTHLY_TABLE_PATH
	graph_path: str = G_YEARLY_TWLEN_GRAPH_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

	# graph settings
	graph_title: str = "ユーザの利用年数によるグループ分け"
	graph_xlabel: str = "投稿した年月"
	graph_ylabel: str = "グループごとの割合[%]"
	colors = {
		'0': 'darkorchid',
		'1': 'royalblue',
		'2': 'orangered',
		'3': 'forestgreen',
		'4': 'crimson',
	}

def draw_bar(args, start_year, start_month, end_year, end_month):
	start_num = (start_year - 2012) * 12 + (start_month - 1)
	end_num = (end_year - 2012) * 12 + (end_month - 1)
	plt.axvspan(start_num, end_num, color='lightgreen', alpha=0.5)

def main(args):
	for toxic in args.toxic_label + ['all']:
		table_file = os.path.join(args.table_path, f"{toxic}.csv")
		graph_file = os.path.join(args.graph_path, f"{toxic}.png")
		df = pd.read_csv(table_file, index_col=0)
		df = df[df.index.str.split('-').str[0].isin(args.years)]
		# 欠損月を0埋め
		for year in args.years:
			for month in range(1, 12+1):
				id = f"{year}-{str(month).zfill(2)}"
				if id not in df.index:
					df.loc[id] = [0 for _ in range(len(df.columns))]
					# print('Added id: ', id)
		if not 'all' in df.columns:
			df['all'] = df.sum(axis=1)
		for group in args.groups:
			df[str(group)] = df[str(group)]/df['all']*100
		df = df.sort_index().drop('all', axis=1)
		# print("id: ", list(df.index))
		print(df)
		plt.figure()
		df.plot.bar(stacked=True)
		plt.xticks(
			range(0, 12*len(args.years)+1, 12),
			args.years + [""],
			rotation=0
		)


		# 投稿数が異常に多い月を強調表示
		# 2012-01, 2013-03
		draw_bar(args, 2012, 1, 2013, 3)

		# 2019-5, 2020-12
		draw_bar(args, 2019, 5, 2020, 12)

		plt.legend().remove()
		# plt.legend(loc='lower right')
		# plt.title(f"{args.graph_title} ({toxic})")
		# plt.xlabel(args.graph_xlabel)
		# plt.ylabel(args.graph_ylabel)
		plt.tight_layout()
		plt.savefig(graph_file)
		plt.close()

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

