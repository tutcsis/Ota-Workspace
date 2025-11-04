import os
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	table_path: str = "/work/s245302/Ota-Workspace/tables/twlength_tweet_count/"
	graph_path: str = "/work/s245302/Ota-Workspace/imgs/twlength_tweet_count/"
	toxic_label: list = ["obscene", "discriminatory", "violent"]
	years: list = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
	twcounts: list = ['le20', 'le40', 'le60', 'le80', 'le100', 'le120', 'le140', 'g140', 'all']

	# graph settings
	graph_title: str = "twcounted Toxic Tweet Count"
	graph_xlabel: str = "month"
	graph_ylabel: str = "tweets"
	colors = {
		'le20': 'darkorchid',
		'le40': 'royalblue',
		'le60': 'orangered',
		'le80': 'forestgreen',
		'le100': 'crimson',
		'le120': 'gold',
		'le140': 'teal',
		'g140': 'coral',
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
		for twcount in args.twcounts:
			df[str(twcount)] = df[str(twcount)]/df['all']*100
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
		plt.legend(bbox_to_anchor=(1, 1))
		plt.xlabel(args.graph_xlabel)
		plt.ylabel(args.graph_ylabel)
		plt.tight_layout()
		plt.savefig(graph_file)
		plt.close()

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

