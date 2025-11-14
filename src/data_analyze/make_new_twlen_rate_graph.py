from pathes import (
	NEW_TOXIC_TW_COUNT_PATH,
	TOXIC_TWLEN_COUNT_GRAPH_PATH,
	TOXIC_LABEL,
	USE_YEARS,
	GROUP
)
import utils
import os
import json
import matplotlib.pyplot as plt
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	table_path: str = NEW_TOXIC_TW_COUNT_PATH
	graph_path: str = TOXIC_TWLEN_COUNT_GRAPH_PATH
	table_columns: list = ['1', '2', 'all']
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

	# graph settings
	graph_title: str = "twlength Toxic Tweet Count"
	graph_xlabel: str = "month"
	graph_ylabel: str = "tweets"
	colors = {
		'1': 'royalblue',
		'2': 'orangered',
		'all': 'sienna'
	}

def main(args):
	for toxic in args.toxic_label:
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
		
		for group in args.table_columns:
			df[group] = df[group]/df['all']*100
		df = df.sort_index().drop('all', axis=1)
		print(df)
		
		# plotting
		fig, ax = plt.subplots(figsize=(12, 6))
		ax.plot(df.index, df['1'], marker='o', color=args.colors['1'], label='group 1')
		ax.set_yticks(range(0, 101, 10))
		ax.grid(True, axis='both', linestyle='--')
		year_labels = [f"{year}-01" for year in args.years]
		ax.set_xticks([label for label in df.index if label in year_labels])
		ax.set_xticklabels(args.years)

		ax.set_title(f"{args.graph_title} Rate (%) ({toxic})")
		ax.set_xlabel(args.graph_xlabel)
		ax.set_ylabel(args.graph_ylabel)
		ax.legend()

		# plt.figure()
		# df.plot.bar(stacked=True)
		# plt.xticks(
		# 	range(0, 12*len(args.years)+1, 12),
		# 	args.years + [""]
		# )
		# plt.title(f"{args.graph_title} ({toxic})")
		# plt.legend(bbox_to_anchor=(1, 1))
		# plt.xlabel(args.graph_xlabel)
		# plt.ylabel(args.graph_ylabel)
		
		plt.tight_layout()
		plt.savefig(graph_file)
		plt.close()

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
