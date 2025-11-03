from pathes import (
	GROUPED_TOXIC_COUNTS_PATH,
	GROUPED_MONTHLY_COUNTS_PATH,
	GROUPED_COUNTS_GRAPH_PATH,
	TOXIC_LABEL,
	USE_YEARS,
	GROUP
)
import utils
import os
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	table_path: str = GROUPED_MONTHLY_COUNTS_PATH
	graph_path: str = GROUPED_COUNTS_GRAPH_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

	# graph settings
	graph_title: str = "Grouped Toxic Tweet Count"
	graph_xlabel: str = "month"
	graph_ylabel: str = "tweets"
	colors = {
		'0': 'darkorchid',
		'1': 'royalblue',
		'2': 'orangered',
		'3': 'forestgreen',
		'4': 'crimson',
		'all': 'sienna'
	}
	ax1_ymax = {
		"violent": 500,
		"discriminatory": 150,
		"obscene": 600,
		"all": 2000
	}
	ax2_ymax = {
		"violent": 25000,
		"discriminatory": 7500,
		"obscene": 30000,
		"all": 60000
	}


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
		for group in args.groups:
			df[str(group)] = df[str(group)]/df['all']*100
		df = df.sort_index().drop('all', axis=1)
		# print("id: ", list(df.index))
		print(df)
		plt.figure()
		df.plot.bar(stacked=True)
		plt.xticks(
			range(0, 12*len(args.years)+1, 12),
			args.years + [""]
		)
		plt.title(f"{args.graph_title} ({toxic})")
		plt.xlabel(args.graph_xlabel)
		plt.ylabel(args.graph_ylabel)
		plt.tight_layout()
		plt.savefig(graph_file)
		plt.close()


if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

