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
	USE_YEARS,
	GROUP
)
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	table_path: str = "tables/new_group_analyze/2-2_textlen_group/"
	graph_path: str = "imgs/new_group_analyze/2-3_textlen_group/"
	table_columns: list = ['1', '2', 'all']
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	groups: list = GROUP

	# graph settings
	graph_title: str = "投稿の文字数によるグループ分け"
	graph_xlabel: str = "投稿した年月"
	graph_ylabel: str = "グループ 1 の割合"
	colors = {
		'1': 'royalblue',
		'2': 'orangered',
		'all': 'sienna'
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
		
		for group in args.table_columns:
			df[group] = df[group]/df['all']*100
		df = df.sort_index().drop('all', axis=1)
		print(df)
		
		# plotting
		plt.figure()
		plt.plot(df.index, df['1'], marker='o', color='black', linewidth=1, markersize=5)
		plt.fill_between(df.index, df['1'], color='blue', alpha=0.1, label="短文投稿")  # 線の下側を青色で塗りつぶし
		plt.fill_between(df.index, df['1'], 100, color='red', alpha=0.1, label="長文投稿")  # 線の上側を赤色で塗りつぶし
		plt.ylim(0, 100)
		plt.yticks(range(0, 101, 10))
		# ax.grid(True, axis='both', linestyle='--')

		plt.title(f"{args.graph_title} ({toxic})")
		plt.xlabel(args.graph_xlabel)
		plt.ylabel(args.graph_ylabel)
		# plt.legend()
		# plt.legend().remove()
		plt.xticks(
			range(0, 12*len(args.years)+1, 12),
			args.years + [""],
			rotation=0
		)
		plt.grid()
		# plt.legend(bbox_to_anchor=(1, 1))
		plt.legend(loc='lower right')

		# df.plot.bar(stacked=True)
		
		plt.tight_layout()
		plt.savefig(graph_file)
		plt.close()

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
