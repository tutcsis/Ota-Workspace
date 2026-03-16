import random
import os
import json
from pathlib import Path
from tap import Tap

class Args(Tap):
	# dataset_path: str = "data/twitter_stream/text-archive_ja/2012-02/"
	# output_path: str = "data/twitter_stream/text-archive_ja/sampling/"
	# month: str = "2012-02"

	dataset_path: str = ""
	output_path: str = ""
	month: str = ""

	sample_len: int = 100

def main(args):
	print(f"dataset_path: {args.dataset_path}, output_path: {args.output_path}, month: {args.month}")
	samples = []
	json_files = [f for f in os.listdir(args.dataset_path) if f.endswith('.json')]
	for json_file in json_files:
		file_path = os.path.join(args.dataset_path, json_file)
		with open(file_path, 'r', encoding='utf-8') as f:
			data = json.load(f)
			sample_keys = random.sample(list(data.keys()), min(args.sample_len, len(data)))
			print(f"json_file: {json_file}")
			for k in sample_keys:
				samples.append({
					"tweet_id": k,
					"text": data[k],
          "time": json_file.split('.json')[0],
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

