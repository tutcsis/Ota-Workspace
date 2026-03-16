import collections
import json
from tap import Tap

class Args(Tap):
	input_file: str = "data/twitter_stream/toxic-archive_ja/sampling/2014-06.jsonl"
	target_toxic_labels: list = ["personal", "violent", "discriminatory"]
	search_phrase: str = "@mikan_powder711 あぁ＾"

def calc_top_n_toxic_tweet(args, toxic_label, text_len=10, n=10):
	print(f"toxic label: {toxic_label}")
	words = []
	with open(args.input_file, 'r') as f:
		for line in f:
			tweet = json.loads(line)
			if tweet[toxic_label] == 1:
				words.append(tweet['text'][:text_len])
	word_counter = collections.Counter(words)
	print(f"=== Top {n} Toxic Tweet Beginnings ===")
	for word, count in word_counter.most_common(n):
		print(f"{word}: {count}")

def main(args):
	for toxic_label in args.target_toxic_labels:
		# calc_top_n_toxic_tweet(args, toxic_label, text_len=20, n=20)
  
		# 特定のフレーズを含む有害ツイートの集計
		words = []
		with open(args.input_file, 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if args.search_phrase in tweet['text'] and tweet[toxic_label] == 1:
					words.append(tweet['text'][:30])
		word_counter = collections.Counter(words)
		print(f"=== Tweets containing '{args.search_phrase}' with label '{toxic_label}' ===")
		for word, count in word_counter.most_common(10):
			print(f"{word}: {count}")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
