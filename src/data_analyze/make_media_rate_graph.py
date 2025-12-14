from pathes import (
	TOXIC_MEDIA_TABLE_PATH,
	TOXIC_MEDIA_GRAPH_PATH,
	ALL_MEDIA_TABLE,
	ALL_MEDIA_GRAPH_PATH,
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
	toxic_media_table_folder: str = TOXIC_MEDIA_TABLE_PATH
	toxic_media_graph_folder: str = TOXIC_MEDIA_GRAPH_PATH
	all_media_table_file: str = ALL_MEDIA_TABLE
	all_media_graph_file: str = ALL_MEDIA_GRAPH_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = ["url", "media", "both", "other"]

	# graph settings
	graph_title: str = "メディア・URLの有無によるグループ分け"
	graph_xlabel: str = "投稿した年月"
	graph_ylabel: str = "グループごとの割合[%]"
	colors = {
		'url': 'darkorchid',
		'media': 'royalblue',
		'both': 'orangered',
		'other': 'forestgreen',
	}

def draw_bar(args, start_year, start_month, end_year, end_month):
	start_num = (start_year - 2012) * 12 + (start_month - 1)
	end_num = (end_year - 2012) * 12 + (end_month - 1)
	plt.axvspan(start_num, end_num, color='lightsalmon', alpha=0.5)

def make_graph(args, file_path, graph_file, toxic=None):
	df = pd.read_csv(file_path, index_col=0)
	
	# change values to percentage
	for group in args.groups:
		df[str(group)] = df[str(group)]/df['all']*100
	df = df.drop('all', axis=1)
	# print(df)

	# make graph
	plt.figure()
	df.plot.bar(stacked=True, color=[args.colors[str(g)] for g in args.groups])
	
	# 投稿数が異常に多い月を強調表示
	# 2012-01, 2013-03
	draw_bar(args, 2012, 1, 2013, 3)

	# 2019-5, 2020-12
	draw_bar(args, 2019, 5, 2020, 12)


	# plt.title(f"{args.graph_title} ({toxic})")
	plt.legend().remove()
	# plt.legend(bbox_to_anchor=(1, 1))
	# plt.xlabel(args.graph_xlabel)
	# plt.ylabel(args.graph_ylabel)
	plt.xticks(
		range(0, 12*len(args.years)+1, 12),
		args.years + [""],
		rotation=0
	)
	plt.tight_layout()
	plt.savefig(graph_file)
	plt.close()


def main(args):
	print(f"toxic_media_table_folder: {args.toxic_media_table_folder}")
	print(f"toxic_media_graph_folder: {args.toxic_media_graph_folder}")

	# toxic grouped table to graph
	for toxic in args.toxic_label:
		table_file = os.path.join(args.toxic_media_table_folder, f"{toxic}.csv")
		graph_file = os.path.join(args.toxic_media_graph_folder, f"{toxic}.png")
		make_graph(args, table_file, graph_file, toxic)

	# all grouped table to graph
	make_graph(args, args.all_media_table_file, args.all_media_graph_file)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
