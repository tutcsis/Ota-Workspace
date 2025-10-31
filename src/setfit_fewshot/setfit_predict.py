from datasets import load_dataset, Dataset
from setfit import (
	SetFitModel,
	Trainer,
	TrainingArguments,
	sample_dataset
)
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np

import json
from datetime import datetime
from pathlib import Path
from tap import Tap
from typing import Literal
from collections import Counter

class Args(Tap):
	# dataset_path: str = "data/twitter_stream/text-archive_ja/sampling/2011-09.jsonl"
	# output_path: str = "data/twitter_stream/toxic-archive_ja/sampling/2011-09.jsonl"
	dataset_path: str = ""
	output_path: str = ""

	num_labels: int = 2
	max_length: int = 1024

	model_name: str = "cl-nagoya/ruri-v3-310m"
	trained_model_path: str = "models/few-shot/ruri-v3-310m_len1024_yesno4"
	output_dir: str = ""

	datasplit_rate: float = 0.3
	datasplit_seed: int = 42

	batch_size: str = 60000

	sampling_strategy: Literal["oversampling", "undersampling", "unique"] = "oversampling"
	target_strategy: Literal["one-vs-rest", "multi-output", "classifier-chain"] = "multi-output"

	device: Literal["cuda", "cpu"] = "cuda" if torch.cuda.is_available() else "cpu"
	suppress_dynamo_errors: bool = True
	debug: bool = True

	def process_args(self):
		if self.output_dir:
			self.output_dir = Path( self.output_dir )
		else:
			basename = self.model_name.split("/")[-1]
			date, time = datetime.now().strftime("%Y-%m-%d/%H-%M-%S.%f").split("/")
			output_dir = Path("outputs", basename, date, time)
			self.output_dir = output_dir
		self.output_dir.mkdir(parents=True)
		log_path = Path( self.output_dir, "parameters.txt" )
		self.log_file = log_path.open( mode='w', buffering=1 )
		print( json.dumps({ "dataset_path": self.dataset_path,
					"model_name": self.model_name }),
					file=self.log_file )


	def training_args(self):
		x = TrainingArguments(
			output_dir=self.output_dir,
			sampling_strategy=self.sampling_strategy,
			batch_size=self.batch_size,
			num_epochs=self.num_epochs,
			logging_dir=self.output_dir,
		)
		print(json.dumps(x.to_dict(), default=str), file=self.log_file)
		return x

def main(args):
	def truncation_text(example):
		example["text"] = example["text"][:args.max_length]

	with open(args.dataset_path) as f:
		dict_list = [json.loads(line) for line in f]
	
	# dataset = Dataset.from_dict({
	# 	"tweet_id": list(int(k) for k in sampled_dict.keys()),
	# 	"text": list(sampled_dict.values())
	# })
	dataset = Dataset.from_dict({
		"tweet_id": [item["tweet_id"] for item in dict_list],
		"user_id": [item["user_id"] for item in dict_list],
		"screen_name": [item["screen_name"] for item in dict_list],
		"text": [item["text"] for item in dict_list],
		"time": [item["time"] for item in dict_list],
		"month": [item["month"] for item in dict_list]
	})
	print(dataset)
	dataset = dataset.map(truncation_text)

	if args.suppress_dynamo_errors:
		import torch._dynamo
		# torch._dynamo.config.suppress_errors = True
		torch._dynamo.disable()

	model = SetFitModel.from_pretrained(
		args.trained_model_path,
		multi_target_strategy=args.target_strategy,
		device=args.device
	)

	results = []
	for i in range(0, dataset.num_rows, args.batch_size):
		batch = dataset.select(range(i, min(i + args.batch_size, dataset.num_rows)))
		batch_results = model.predict(batch["text"]).numpy()
		results.append(batch_results)
	results = np.vstack(results)

	# results = model.predict(dataset["text"]).numpy()

	with open(f"{args.trained_model_path}/categories.txt") as f2:
		categories = [s.strip() for s in f2.readline().split(',')]
		print('categories: ', categories)
	
	# results = []
	# with open(args.output_path) as f:
	# 	for line in f:
	# 		results.append(np.array([int(x) for x in line.split(',')]))
	# results = np.vstack(results)
	# print('results: ', results)
	# print(results.shape)

	for i, category in enumerate(categories):
		dataset = dataset.add_column(category, results[:,i].tolist())
	print(dataset)
	dataset_list = [
		{key: row[key] for key in dataset.features.keys()}
		for row in dataset
	]
	# print(dataset_list[:3])

	with open(args.output_path, "w", encoding="utf-8") as outf:
		for item in dataset_list:
			outf.write(json.dumps(item, ensure_ascii=False) + '\n')

	print("Prediction completed successfully!")



if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

