from pathes import (
	G_TWLEN_TABLE_PATH,
	G_TWLEN_GRAPH_PATH,
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
	g_twlen_table_folder: str = G_TWLEN_TABLE_PATH
	g_twlen_graph_folder: str = G_TWLEN_GRAPH_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

	# graph settings
	graph_title: str = "Grouped Toxic Tweet Length"
	graph_xlabel: str = "year"
	graph_ylabel: str = "tweet counts"
	colors = {
		'0': 'darkorchid',
		'1': 'royalblue',
		'2': 'orangered',
		'3': 'forestgreen',
		'4': 'crimson',
	}

def main(args):
	print(f"g_twlen_table_folder: {args.g_twlen_table_folder}")
	print(f"g_twlen_graph_folder: {args.g_twlen_graph_folder}")

	for toxic in args.toxic_label:
		table_file = os.path.join(args.g_twlen_table_folder, f"{toxic}.csv")
		graph_file = os.path.join(args.g_twlen_graph_folder, f"{toxic}.png")
		df = pd.read_csv(table_file, index_col=0, dtype=np.int64)
		
		# change values to percentage
		for group in args.groups:
			df[str(group)] = df[str(group)]/df['all']*100
		df = df.drop('all', axis=1)
		# print(df)

		# make graph
		plt.figure()
		df.plot.bar(stacked=True, color=[args.colors[str(g)] for g in args.groups])
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
