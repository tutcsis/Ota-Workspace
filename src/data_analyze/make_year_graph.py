import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
from tap import Tap

class Args(Tap):
	table_path: str = "tables/ja_tweet_counts.csv"
	# table_path: str = "tables/merged_toxic_count_with_all_tweets.csv"
	# table_path: str = "tables/1000tweet_toxic_count.csv"
	# table_path: str = "tables/tweet_toxic_count.csv"
	# graph_path: str = "imgs/1000tweets_2012-2020_3toxic.png"
	# graph_path: str = "imgs/1000tweets_toxic_rate/"
	# graph_path: str = "imgs/year_1000tweets_3toxic.png"
	# graph_path: str = "imgs/year1000tweets_2012-2020_3toxic.png"
	# graph_path: str = "imgs/1000tweets_2012-2020_3toxic_rate.png"
	graph_path: str = "imgs/2012-2020_ja_twlen.png"

	user_years: list = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]

	graph_labels: list = ["obscene", "discriminatory", "violent"]
	graph_title: str = "全体の投稿数"
	# graph_title: str = "有害投稿数"
	# graph_xlabel: str = "month"
	graph_xlabel: str = "投稿した年月"
	graph_y1label: str = "有害投稿の割合"
	graph_y2label: str = "投稿数"
	rate: bool = True
	mode: str = "all" # all, toxic
	# mode: str = "toxic" # all, toxic
	toxic_limit: int = 5

def draw_bar(args, start_year, start_month, end_year, end_month):
	start_num = (start_year - 2012) * 12 + (start_month - 1)
	end_num = (end_year - 2012) * 12 + (end_month - 1)
	plt.axvspan(start_num, end_num, color='lightgreen', alpha=0.5)

def make_tweet_graph(args, df, year=None):
	if year == 'avg':
		df['year'] = df.index.str.split('-').str[0]
		df = df.groupby('year').mean()
	elif year:
		df = df[df.index.str.startswith(year)]

	# スパム投稿を除外
	if args.mode == 'toxic':
		for toxic in args.graph_labels:
			# 欠損値は 0 で割らないようにする
			df.loc[df['total'] != 0, toxic] = df[toxic] / df['total'] * 100
			df[toxic] = df[toxic].apply(lambda x: x if x <= args.toxic_limit else args.toxic_limit)
		print(df.head()[args.graph_labels + ['total']])
		# return
	

	if args.rate:
		print("Plotting rate graph[%]")
		plt.figure()
		if args.mode == 'toxic':
			for toxic in args.graph_labels:
				plt.plot(df.index, df[toxic], label=toxic, marker='o')
		elif args.mode == 'all':
			plt.plot(df.index, df['alltweets'], label='alltweets', marker='o', color='black')
		plt.xticks(
			range(0, 12*len(args.user_years)+1, 12),
			args.user_years + [""]
		)

		# 投稿数が異常に多い月を強調表示
		# 2012-01, 2013-03
		draw_bar(args, 2012, 1, 2013, 3)

		# 2019-5, 2020-12
		draw_bar(args, 2019, 5, 2020, 12)

		plt.grid(True)
		# plt.legend()
		# plt.title(f"{args.graph_title}")
		# plt.xlabel(args.graph_xlabel)
		# if args.mode == 'toxic':
		# 	plt.ylabel(f"{args.graph_y1label}[%]")
		# elif args.mode == 'all':
		# 	plt.ylabel(f"{args.graph_y2label}")
		plt.tight_layout()
		plt.savefig(args.graph_path)
		plt.close()

	else:
		fig, ax1 = plt.subplots(figsize=(10, 6))
		for label in args.graph_labels:
			ax1.plot(df.index, df[label], label=label, marker='o')
		# グリッドの名前を設定
		if year == 'avg':
			ax1.set_xticks(range(0, len(args.user_years)+1))
			ax1.set_xticklabels(args.user_years + [""])
			print("avg")
		elif year:
			ax1.set_xticks(range(0, 12))
			ax1.set_xticklabels([str(i) for i in range(1, 12+1)])
		else:
			ax1.set_xticks(range(0, 12*len(args.user_years)+1, 12))
			ax1.set_xticklabels(args.user_years + [""])

		ax2 = ax1.twinx()
		ax2.plot(df.index, df['alltweets'], label='alltweets', marker='o', color='black')

		ax1.set_xlabel(args.graph_xlabel)
		ax1.set_ylabel(args.graph_y1label)
		ax2.set_ylabel(args.graph_y2label)
		ax1.set_ylim(0, 1e5)
		ax2.set_ylim(0, 2*1e7)

		# ax1, ax2の凡例をまとめる
		lines1, labels1 = ax1.get_legend_handles_labels()
		lines2, labels2 = ax2.get_legend_handles_labels()
		ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

		plt.grid(True)
		plt.tight_layout()
		if year:
			plt.title(f"{args.graph_title} in {year}")
			plt.savefig(f"{args.graph_path}{year}.png")
		else:
			plt.title(args.graph_title)
			plt.savefig(args.graph_path)

def main(args):
	df = pd.read_csv(args.table_path)
	df.set_index('month', inplace=True)
	df = df[df.index.str.split('-').str[0].isin(args.user_years)]
	# 欠損月を0埋め
	for year in args.user_years:
		for month in range(1, 12+1):
			id = f"{year}-{str(month).zfill(2)}"
			if id not in df.index:
				df.loc[id] = [0 for _ in range(len(df.columns))]
				print('Added id: ', id)
	df = df.sort_index()
	# print("id: ", list(df.index))

	# 各年毎のグラフ作成
	# for year in args.user_years:
		# make_tweet_graph(args, df, year)

	# 全年のグラフ作成
	make_tweet_graph(args, df)
	# make_tweet_graph(args, df, year='avg')


if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

