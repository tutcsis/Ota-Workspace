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
					print('Added id: ', id)
		df = df.sort_index()
		print("id: ", list(df.index))
		
		fig, ax1 = plt.subplots()
		
		for group in args.groups[1:]:
			plt.plot(df.index, df[str(group)], label=group, marker='o', color=args.colors[str(group)])

		# グリッドの名前を年に変更
		ax1.set_xticks(range(0, 12*len(args.years)+1, 12))
		ax1.set_xticklabels(args.years + [""])

		ax2 = ax1.twinx()
		for group in ['0', 'all']:
			ax2.plot(df.index, df[group], label=group, marker='o', color=args.colors[group])
		
		ax1.set_xlabel(args.graph_xlabel)
		ax1.set_ylabel(args.graph_ylabel)
		ax2.set_ylabel(args.graph_ylabel + " (group 0 and all)")
		ax1.set_ylim(0, args.ax1_ymax[toxic])
		ax2.set_ylim(0, args.ax2_ymax[toxic])

		lines1, labels1 = ax1.get_legend_handles_labels()
		lines2, labels2 = ax2.get_legend_handles_labels()
		ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

		plt.title(args.graph_title)
		plt.grid(True)
		plt.tight_layout()
		plt.savefig(graph_file)


if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

