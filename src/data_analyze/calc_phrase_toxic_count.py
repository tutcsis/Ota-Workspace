import json
from tap import Tap

class Args(Tap):
	input_file: str = "data/twitter_stream/toxic-archive_ja/sampling/2014-06.jsonl"
	# search_phrase: str = "@TKYKSN 気取り死ね"
	# search_phrase: str = "@mikan_powder711 あぁ＾～"
	search_phrase: str = "@r7L 爆撃乞食きめえｗｗｗｗ"

def main(args):

	# ラベルの初期化
	labels = {
		'personal': 0,
		'others': 0,
		'illegal': 0,
		'corporate': 0,
		'violent': 0,
		'discriminatory': 0,
		'obscene': 0
	}

	print("=== Matching Tweets ===")
	all = 0
	with open(args.input_file, 'r') as f:
		for line in f:
			tweet = json.loads(line)
			if args.search_phrase in tweet['text']:
				# print(f"Text: {tweet['text']}")
				# ラベルの集計
				all += 1
				for label in labels.keys():
					labels[label] += tweet[label]

	print("\n=== Label Counts ===")
	print(f"Total matching tweets: {all}")
	for label, count in labels.items():
		print(f"{label}: {count}")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
