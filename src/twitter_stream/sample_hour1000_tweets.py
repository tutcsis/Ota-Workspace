import random
import os
import json
from pathlib import Path
from tap import Tap

class Args(Tap):
	dataset_path: str = ""
	output_path: str = ""
	month: str = ""

	sample_len: int = 1000

def count_lines(path):
	count = 0
	with open(path, "r") as f:
		for _ in f:
			count += 1
	return count

def main(args):
	print(f"dataset_path: {args.dataset_path}, output_path: {args.output_path}, month: {args.month}")
	samples = []
	files = [f for f in os.listdir(args.dataset_path) if f.endswith('.txt')]
	for file in files:
		file_path = os.path.join(args.dataset_path, file)
		tweet_len = count_lines(file_path)
		sample_keys = random.sample(range(tweet_len), min(args.sample_len, tweet_len))
		with open(file_path, 'r', encoding='utf-8') as f:
			for i, line in enumerate(f):
				if i in sample_keys:
					tweet_id, json_str = line.strip().split("\t")
					json_data = json.loads(json_str)
					samples.append({
						"tweet_id": tweet_id,
						"text": repr(json_data["text"])[1:-1],
						"user_id": json_data["user"]["id"],
						"screen_name": json_data["user"]["screen_name"],
						"time": file.split('.txt')[0],
						"month": args.month
					})
	output_file = os.path.join(args.output_path, f"{args.month}.jsonl")
	with open(output_file, 'w', encoding='utf-8') as outf:
		for sample in samples:
			outf.write(json.dumps(sample, ensure_ascii=False) + '\n')
	print(f"Saved {len(samples)} samples to {output_file}")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

