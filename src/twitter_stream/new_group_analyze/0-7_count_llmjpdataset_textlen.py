import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
import json
from tap import Tap
from collections import defaultdict

class Args(Tap):
	dataset_path: str = "data/llmjp_toxicity_dataset/toxicity_dataset_ver2.jsonl"
	table_path: str = "tables/new_group_analyze/0-7_llmjpdataset_textlen.csv"
	# graph_path: str = "imgs/new_group_analyze/0-7_llmjpdataset_textlen.png"

	label_mode = False
	graph_title: str = "すべての投稿数"
	graph_xlabel: str = "投稿した年月"
	graph_ylabel: str = "投稿数"


def main(args):
	dict_idx = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
	char_count_dict = dict([(idx, 0) for idx in dict_idx])
	rate = 1
	with open(args.dataset_path, 'r', encoding='utf-8') as f:
		for line in f:
			data = json.loads(line)
			if 'text' in data:
				text_length = len(data['text'])
				if text_length <= 100:
					bucket = 0
				elif text_length <= 1000:
					bucket = ((text_length-1) // 100) * 100
				else:
					bucket = 1000
				char_count_dict[bucket] += 1

	# 結果をCSVファイルに保存
	df = pd.DataFrame(list(char_count_dict.items()), columns=['text_length_bucket', 'count'])
	df = df.sort_values('text_length_bucket').reset_index(drop=True)
	df.to_csv(args.table_path, index=False)


if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

