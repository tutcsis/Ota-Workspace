# 現在はlang=jaが一つでも含まれている行を抽出しているが、これがどの程度正しいかを確かめる
# そこで、日本語として抽出されたものを my_jp_label, 真に日本語のものを gold_jp_label としてラベル付けをする
# 最終的に、my_pos, my_neg, gold_pos, gold_neg の4つのカウントを出力する

import json
import os
import random
import utils
from tap import Tap
from tqdm import tqdm

class Args(Tap):
	# フォルダの内部構造：yyyy-mm -> yyyy-mm-dd-hh.txt
	all_lang_archive: str = "/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive-twitterstream/"
	ja_filtered_archive: str = "/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/"
	out_table: str = "/work/s245302/Ota-Workspace/tables/check_ja_tweets/"
	# out_table: str = "/work/s245302/Ota-Workspace/tables/ja_tweet_check_results.csv"
	month: str = ""

	sample_len: int = 100

def count_lines(path):
	count = 0
	with open(path, "r") as f:
		for _ in f:
			count += 1
	return count

def count_month_ja_tweets(args, month_folder):
	month_path = os.path.join(args.all_lang_archive, month_folder)
	gold_pos, gold_neg = 0, 0
	pos_pos, pos_neg, neg_pos, neg_neg = 0, 0, 0, 0
	for hour_file in utils.get_file_names(month_path):
		hour_path = os.path.join(month_path, hour_file)
		my_hour_path = os.path.join(args.ja_filtered_archive, month_folder, hour_file)
		
		line_counts = count_lines(hour_path)
		sample_keys = random.sample(range(line_counts), min(args.sample_len, line_counts))

		pos_tw_ids, neg_tw_ids = set(), set()

		with open(hour_path, 'r') as f:
			for i, line in enumerate(f):
				if i not in sample_keys:
					continue
				tw_id, tweet = line.split('\t')
				tweet_json = json.loads(tweet)
				lang = tweet_json.get('lang', '')
				if not lang:
					lang = tweet_json.get('user', {}).get('lang', '')
				if lang == 'ja':
					pos_tw_ids.add(tw_id)
				else:
					neg_tw_ids.add(tw_id)
	

		curr_pos_pos, curr_neg_pos = 0, 0
		with open(my_hour_path, 'r') as f:
			for line in f:
				tw_id, tweet = line.split('\t')
				if tw_id in pos_tw_ids:
					curr_pos_pos += 1

				if tw_id in neg_tw_ids:
					curr_neg_pos += 1

		gold_pos += len(pos_tw_ids)
		gold_neg += len(neg_tw_ids)
		pos_pos += curr_pos_pos
		neg_pos += curr_neg_pos
		pos_neg += len(pos_tw_ids) - curr_pos_pos
		neg_neg += len(neg_tw_ids) - curr_neg_pos

	# print(f"gold_pos: {gold_pos}, gold_neg: {gold_neg}")
	# print(f"pos_pos: {pos_pos}, pos_neg: {pos_neg}, neg_pos: {neg_pos}, neg_neg: {neg_neg}")
	return gold_pos, gold_neg, pos_pos, pos_neg, neg_pos, neg_neg

def main(args):
	# 全言語のファイルから、真に日本語のものを抽出(tweet_id)
	# rows = []

	gold_pos, gold_neg, pos_pos, pos_neg, neg_pos, neg_neg = count_month_ja_tweets(args, args.month)
	out_txt = f"{args.month},{gold_pos},{gold_neg},{pos_pos},{pos_neg},{neg_pos},{neg_neg}"
	with open(f"{args.out_table}/{args.month}.txt", "w") as f:
		f.write(out_txt + "\n")

	# すべての月について集計
	# for month_folder in tqdm(utils.get_folder_names(args.all_lang_archive)):
	# 	gold_pos, gold_neg, pos_pos, pos_neg, neg_pos, neg_neg = count_month_ja_tweets(args, month_folder)
		# rows.append({
		# 	"month": month_folder,
		# 	"gold_pos": gold_pos,
		# 	"gold_neg": gold_neg,
		# 	"pos_pos": pos_pos,
		# 	"pos_neg": pos_neg,
		# 	"neg_pos": neg_pos,
		# 	"neg_neg": neg_neg
		# })

	# out_df = pd.DataFrame(rows)
	# out_df.to_csv(args.out_table, index=False)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
