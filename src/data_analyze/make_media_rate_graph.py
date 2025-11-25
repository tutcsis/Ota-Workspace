from pathes import (
	TOXIC_MEDIA_TABLE_PATH,
	TOXIC_MEDIA_GRAPH_PATH,
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
	toxic_media_table_folder: str = TOXIC_MEDIA_TABLE_PATH
	toxic_media_graph_folder: str = TOXIC_MEDIA_GRAPH_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = ["url", "media", "both", "other"]

	# graph settings
	graph_title: str = "Grouped ALl Tweet Length"
	# graph_title: str = "Grouped Toxic Tweet Length"
	graph_xlabel: str = "year"
	graph_ylabel: str = "tweet counts"
	colors = {
		'url': 'darkorchid',
		'media': 'royalblue',
		'both': 'orangered',
		'other': 'forestgreen',
	}

def main(args):
	print(f"toxic_media_table_folder: {args.toxic_media_table_folder}")
	print(f"toxic_media_graph_folder: {args.toxic_media_graph_folder}")

	# toxic grouped table to graph
	for toxic in args.toxic_label:
		table_file = os.path.join(args.toxic_media_table_folder, f"{toxic}.csv")
		graph_file = os.path.join(args.toxic_media_graph_folder, f"{toxic}.png")
		df = pd.read_csv(table_file, index_col=0)
		
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
		plt.xticks(
			range(0, 12*len(args.years)+1, 12),
			args.years + [""]
		)
		plt.tight_layout()
		plt.savefig(graph_file)
		plt.close()

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
