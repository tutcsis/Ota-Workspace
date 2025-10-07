import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from datasets import load_dataset, Dataset, concatenate_datasets
from setfit import (
	SetFitModel,
	Trainer,
	TrainingArguments,
)
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import numpy as np

import utils
import json
from datetime import datetime
from pathlib import Path
from tap import Tap
from typing import Literal
from collections import Counter
from tqdm import tqdm

class Args(Tap):
	train_path: str = "data/llmjp_toxicity_dataset/train_dataset.jsonl"
	test_path: str = "data/llmjp_toxicity_dataset/test_dataset.jsonl"

	num_labels: int = 2
	max_length: int = 1024

	model_name: str = "cl-nagoya/ruri-v3-310m"
	output_dir: str = ""

	datasplit_rate: float = 0.7
	# datasplit_rate: float = 0.3
	allno_datasplit_rate: float = 0.1
	datasplit_seed: int = 42
	seed: int = 42

	hypothesis: int = 1
	train_no_rate: float = 1.0

	num_samples: int = 8
	num_epochs: int = 1
	batch_size: int = 2
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
		print( json.dumps({
			"train_path": self.train_path,
			"test_path": self.test_path,
			"model_name": self.model_name 
		}), file=self.log_file )

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

	def log(self, metrics: dict) -> None:
		print("metrics: ", metrics)
		print("category_rank: ", self.category_rank)
		log_file = self.output_dir / f"log.csv"
		for category in self.category_rank:
			category_metrics = {
				"category": category,
				"accuracy": metrics[category].get(f"accuracy", -1),
				"precision": metrics[category].get(f"precision", -1),
				"recall": metrics[category].get(f"recall", -1),
				"f1": metrics[category].get(f"f1", -1),
				"TN": metrics[category].get("TN", -1),
				"FP": metrics[category].get("FP", -1),
				"FN": metrics[category].get("FN", -1),
				"TP": metrics[category].get("TP", -1),
			}
			utils.log(category_metrics, log_file)
			tqdm.write(
				f"category: {category} \t"
				f"accuracy: {category_metrics[f'accuracy']:.4f} \t"
				f"precision: {category_metrics[f'precision']:.4f} \t"
				f"recall: {category_metrics[f'recall']:.4f} \t"
				f"f1: {category_metrics[f'f1']:.4f} \t"
				f"TN: {category_metrics[f'TN']} \t"
				f"FP: {category_metrics[f'FP']} \t"
				f"FN: {category_metrics[f'FN']} \t"
				f"TP: {category_metrics[f'TP']}"
			)
			print(category, "ok!!")

def main(args):
  # 1. Process arguments
	def truncate_text(example):
		example["text"] = example["text"][:args.max_length]
		return example
	
	train_dataset = load_dataset("json", data_files=args.train_path, split="train")
	test_dataset = load_dataset("json", data_files=args.test_path, split="train")
	train_dataset = train_dataset.remove_columns(["label"]).map(truncate_text)
	test_dataset = test_dataset.remove_columns(["label"]).map(truncate_text)
	tasknames = [task for task in train_dataset.column_names if task not in ["id", "text"]]
	label_yes_counts = {taskname: Counter(train_dataset[taskname])["yes"] for taskname in tasknames}
	args.category_rank = [label for (label, _) in sorted(label_yes_counts.items(), key=lambda x: x[1])]
	# Category rank: ['others', 'personal', 'illegal', 'violent', 'discriminatory', 'corporate', 'obscene']

	def encode_labels(example):
		return {
			"labels": [1 if example[k] == "yes" else 0 for k in args.category_rank]
		}
	train_dataset = train_dataset.map(encode_labels)
	test_dataset = test_dataset.map(encode_labels)
	train_yes_counts = {taskname: Counter(train_dataset[taskname])["yes"] for taskname in tasknames}
	test_yes_counts = {taskname: Counter(test_dataset[taskname])["yes"] for taskname in tasknames}

	if args.debug:
		print("train_dataset:", train_dataset)
		print("test_dataset:", test_dataset)
		print(f"yes_count")
		print(f"- train_yes_counts: {train_yes_counts}")
		print(f"- test_yes_counts: {test_yes_counts}")

	# 3. Train the model
	# 3.1 metrics setup
	def compute_metrics(predictions, labels):
		predictions = np.array(predictions).T
		labels = np.array(labels).T
		metrics = {}
		if args.debug:
			print("category_rank: ", args.category_rank)
		for taskname, _predictions, _labels in zip(args.category_rank, predictions, labels):
		# for taskname, _predictions, _labels in zip(tasknames, predictions, labels):
			label_counts = np.bincount(_labels.astype(int))

			cm = confusion_matrix(_labels, _predictions, labels=[0, 1])
			tn, fp, fn, tp = cm.ravel()
			if args.debug:
				print(f"Confusion Matrix for {taskname}:\n{cm}")
				print(f"label_counts for {taskname}: {label_counts}")
			if cm.shape != (2, 2):
				print(f"Warning: Confusion matrix for {taskname} is not 2x2. It may not be binary classification.")
			metrics[taskname] = {
				"accuracy": accuracy_score(_labels, _predictions),
				"precision": precision_score(_labels, _predictions, zero_division=0),
				"recall": recall_score(_labels, _predictions, zero_division=0),
				"f1": f1_score(_labels, _predictions, zero_division=0),
				"TN": int(tn),
				"FP": int(fp),
				"FN": int(fn),
				"TP": int(tp),
      }
		return metrics

	if args.suppress_dynamo_errors:
		import torch._dynamo
		torch._dynamo.config.suppress_errors = True

	# model, trainer setup
	model = SetFitModel.from_pretrained(
		args.model_name,
		multi_target_strategy=args.target_strategy,
		device=args.device
	)
	trainer = Trainer(
		model=model,
		args=args.training_args(),
		train_dataset=train_dataset,
		metric=compute_metrics,
		column_mapping={"text": "text", "labels": "label"},
	)
	if args.debug:
		print("trainer: ", trainer)
		print("model: ", model)
	trainer.train()

	# 4. Evaluate the model
	metrics = trainer.evaluate(test_dataset)
	print(metrics)
	args.log(metrics)
	print(f"Metrics saved to, {args.output_dir} / log.csv")
	print("Saving model to", args.output_dir)
	model.save_pretrained(args.output_dir)


if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
