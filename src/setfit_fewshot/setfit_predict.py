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
	dataset_path: str = "data/toxicity_ver2_allyesdata.jsonl"
	corpus_dir: str = "data/CC-MAIN-2023-23/CC-MAIN-20230527223515-20230528013515/"
	corpus_path: str = corpus_dir+"00000-ja-sentence.txt"
	output_labels_path: str = corpus_dir+"00000-ja-labels.txt"
	num_labels: int = 2
	max_length: int = 256

	corpus_release: str = ""
	group: str = ""
	file_count: int = 0

	model_name: str = "cl-nagoya/ruri-v3-310m"
	trained_model_path: str = "outputs/ruri-v3-310m/2025-06-19/14-47-07.781974"
	# trained_model_path: str = "outputs/ruri-v3-310m/2025-06-14/18-04-34.477448/checkpoint-3341"
	output_dir: str = ""

	datasplit_rate: float = 0.3
	datasplit_seed: int = 42


	num_samples: int = 32
	num_epochs: int = 1
	batch_size: int = 8
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
	print("corpus_time: ", args.corpus_release)
	print("group: ", args.group)
	print("file_count: ", args.file_count)

	for i in range(args.file_count):
		ja_text_path = f"data/{args.corpus_release}/{args.group}/{i:05d}-ja-sentence.txt"
		ja_out_label_path = f"prediction_data/{args.corpus_release}/{args.group}/{i:05d}-ja-label.txt"

		# read corpus dataset
		with open(ja_text_path, "r", encoding="utf-8") as f:
			texts = [line.strip() for line in f.readlines()]
		corpus_dataset = Dataset.from_dict({"text": texts})
		def truncate_text(example):
			example["text"] = example["text"][:args.max_length]
			return example
		corpus_dataset = corpus_dataset.map(truncate_text)

		if args.suppress_dynamo_errors:
			import torch._dynamo
			# torch._dynamo.config.suppress_errors = True
			torch._dynamo.disable()

		# read setfit trained model
		model = SetFitModel.from_pretrained(
			args.trained_model_path,
			multi_target_strategy=args.target_strategy,
			device=args.device
		)

		# if args.debug:
		# 	# print("text sample: ", corpus_dataset["text"][:args.batch_size])
		# 	print("Model loaded succece!! \n model: ", model)

		# predict
		predict_list = list(corpus_dataset["text"])
		# print(type(predict_list), predict_list)
		results = model.predict(predict_list)

		with open(ja_out_label_path, "w", encoding="utf-8") as outf:
			results = results.numpy()
			for row in results:
				outf.write(f"{','.join(map(str, row))}\n")

		print("Prediction completed successfully!")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

