import os
import json
import matplotlib.pyplot as plt
import japanize_matplotlib
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import utils
from pathes import (
	TOXIC_LABEL,
	USE_YEARS
)
from tap import Tap

class Args(Tap):
	toxic_table: str = "tables/new_group_analyze/4-2_machine_group/"
	toxic_graph: str = "imgs/new_group_analyze/4-3_machine_graph/"
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = ["iphone", "ipad", "android", "web", "other"]

	# graph settings
	colors = {
		'iphone': 'deepskyblue',
		'ipad': 'dodgerblue',
		'android': 'limegreen',
		'web': 'orange',
		'other': 'gray',
	}
	ymax: int = 20


def make_graph(args, file_path, graph_file, toxic=None):
	df = pd.read_csv(file_path, index_col=0)
	df = df.drop('androidtablet', axis=1)
	
	# change values to percentage
	for machine in args.groups:
		df[str(machine)] = df[str(machine)]/df['all']*100
	df = df.drop('all', axis=1)

	# make graph
	plt.figure()
	df.plot.bar(stacked=True, color=[args.colors[str(m)] for m in args.groups])
	plt.xticks(
		range(0, 12*len(args.years)+1, 12),
		args.years + [""],
		rotation=0
	)
	plt.tight_layout()
	plt.savefig(graph_file)
	plt.close()

def make_line_graph(args, table_path, graph_file, toxic=None):
	df = pd.read_csv(table_path, index_col=0)
	df = df.drop('androidtablet', axis=1)
	
	# change values to percentage
	for machine in args.groups:
		df[str(machine)] = df[str(machine)]/df['all']*100
	df = df.drop('all', axis=1)

	# make graph
	plt.figure()
	df.plot(color=[args.colors[str(m)] for m in args.groups])
	plt.xticks(
		range(0, 12*len(args.years)+1, 12),
		args.years + [""],
		rotation=0
	)
	plt.legend(loc='upper right')
	plt.yticks(range(0, 101, 10))
	plt.ylim(0, 100)
	plt.tight_layout()
	plt.savefig(graph_file)
	plt.close()

def make_rate_on_machine_graph(args, table_path, all_table_path, graph_file, toxic=None):
	df = pd.read_csv(table_path, index_col=0)
	df = df.drop('androidtablet', axis=1)
	all_df = pd.read_csv(all_table_path, index_col=0)
	all_df = all_df.drop('androidtablet', axis=1)

	# change values to percentage on iphone
	for machine in args.groups:
		df[machine] = df[machine]/all_df[machine]*100

	# make graph
	plt.figure()
	# df['iphone'].plot(color=args.colors['iphone'], label='iphone')
	df.plot(color=[args.colors[str(m)] for m in args.groups])
	plt.xticks(
		range(0, 12*len(args.years)+1, 12),
		args.years + [""],
		rotation=0
	)
	plt.legend(loc='upper right')
	plt.yticks(range(0, args.ymax+1, 1))
	plt.ylim(0, args.ymax)
	plt.tight_layout()
	plt.savefig(graph_file)
	plt.close()


def main(args):
	print(f"toxic_table: {args.toxic_table}")

	for toxic in args.toxic_label + ['all']:
		table_path = os.path.join(args.toxic_table, f"{toxic}.csv")
		graph_path = os.path.join(args.toxic_graph, f"{toxic}.png")
		# make_graph(args, table_path, graph_path, toxic)
		# make_line_graph(args, table_path, graph_path, toxic)
		if toxic == 'all':
			continue
		make_rate_on_machine_graph(args, table_path, os.path.join(args.toxic_table, "all.csv"), graph_path, toxic)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
