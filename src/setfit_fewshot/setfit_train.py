# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datasets import load_dataset, Dataset, concatenate_datasets
from setfit import (
	SetFitModel,
	Trainer,
	TrainingArguments,
	sample_dataset
)
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import numpy as np

import utils
import random
import json
from datetime import datetime
from pathlib import Path
from tap import Tap
from typing import Literal
from collections import Counter
from tqdm import tqdm

class Args(Tap):
	yes_dataset_path: str = "data/toxicity_ver2_allyesdata.jsonl"
	allno_data_path: str = "data/toxicity_ver2_allnodata.jsonl"
	corpus_path: str = "data/CC-MAIN-2023-23/CC-MAIN-20230527223515-20230528013515/00000-ja-sentence.txt"
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
			"yes_dataset_path": self.yes_dataset_path,
			"no_dataset_path": self.allno_data_path,
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
	
	# 1.1 Loading least toxic yes_dataset
	yes_dataset = load_dataset("json", data_files=args.yes_dataset_path, split="train")
	yes_dataset = yes_dataset.remove_columns(["label"])
	yes_dataset = yes_dataset.map(truncate_text)
	tasknames = [task for task in yes_dataset.column_names if task not in ["id", "text"]]

	# 1.2 Loading non-toxic yes_dataset
	no_dataset = load_dataset("json", data_files=args.allno_data_path, split="train")
	no_dataset = no_dataset.remove_columns(["label"])
	no_dataset = no_dataset.map(truncate_text)
	# if args.debug:
	# 	print("tasknames: ", tasknames)
	# 	print("yes_dataset", yes_dataset)
	# 	print("no_dataset", no_dataset)

	# 1.3 Create category rank list
	label_yes_counts = {taskname: Counter(yes_dataset[taskname])["yes"] for taskname in tasknames}
	args.category_rank = [label for (label, _) in sorted(label_yes_counts.items(), key=lambda x: x[1])]
	if args.debug:
		print("Category: ", tasknames)
		print("label_yes_counts:", label_yes_counts)
		print("Category rank:", args.category_rank)
	# Category rank: ['others', 'personal', 'illegal', 'violent', 'discriminatory', 'corporate', 'obscene']

	# 2. Create train, test dataset from yes_dataset and no_dataset
	# 2.1 split yes_dataset
	yes_dataset = yes_dataset.add_column(name="flag", column=[0]*len(yes_dataset))
	yes_df = yes_dataset.to_pandas()

	for category in args.category_rank:
		print(category)
		# sort df
		yes_df = yes_df.sort_values(by=[category, 'flag'], ascending=False).reset_index(drop=True)

		# count yes num
		yes_count = label_yes_counts[category]
		exist_flag_count = yes_df['flag'].iloc[0:yes_count].sum()
		# print(f"- before flag: {exist_flag_count}, {yes_df['flag'].iloc[0:yes_count].tolist()}")
		# print(f"- {category}: {yes_df[category].iloc[0:yes_count].tolist()}")

		# make random ids list
		set_flag_count = min(args.num_samples, yes_count) - exist_flag_count
		if set_flag_count > 0:
			selected_yes_ids = set(random.sample(
				range(exist_flag_count, yes_count),
				set_flag_count
			))

		# set flag by ids list
		for idx in selected_yes_ids:
			yes_df.at[idx, "flag"] = 1
		# print(f"- selected_yes_ids: {len(selected_yes_ids)}, {selected_yes_ids}")
		# print(f"- after flag: {yes_count}, {yes_df['flag'].iloc[0:yes_count].tolist()}")
		# print("---------------")

	# split by flag
	yes_train_df = yes_df[yes_df["flag"] == 1].reset_index(drop=True)
	yes_test_df = yes_df[yes_df["flag"] == 0].reset_index(drop=True)
	y_train_dataset = Dataset.from_pandas(yes_train_df, features=yes_dataset.features).remove_columns("flag")
	y_test_dataset = Dataset.from_pandas(yes_test_df, features=yes_dataset.features).remove_columns("flag")

	# 2.2 split no_dataset
	# len of each dataset
	yes_len = yes_dataset.num_rows
	no_len = no_dataset.num_rows
	y_train_len = y_train_dataset.num_rows
	y_test_len = y_test_dataset.num_rows
	n_train_len = y_train_len
	n_test_len = min(no_len - n_train_len, int(y_test_len * no_len / yes_len))
	if args.debug:
		print("yes_dataset:", yes_len)
		print("- y_train_dataset:", y_train_len)
		print("- y_test_dataset:", y_test_len)
		print("no_dataset:", no_len)
		print("- n_train_len:", n_train_len)
		print("- n_test_len:", n_test_len)

	no_df = no_dataset.shuffle(seed=args.seed).to_pandas()
	no_train_df = no_df.iloc[-n_train_len:].reset_index(drop=True)
	no_test_df = no_df.iloc[:n_test_len].reset_index(drop=True)
	n_train_dataset = Dataset.from_pandas(no_train_df, features=no_dataset.features)
	n_test_dataset = Dataset.from_pandas(no_test_df, features=no_dataset.features)

	# 2.3 Concatenate yes and no datasets
	train_dataset = concatenate_datasets([y_train_dataset, n_train_dataset])
	test_dataset = concatenate_datasets([y_test_dataset, n_test_dataset])

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
		print(f"- y_train_dataset:", y_train_dataset)
		print(f"- n_train_dataset:", n_train_dataset)
		print("test_dataset:", test_dataset)
		print(f"- y_test_dataset:", y_test_dataset)
		print(f"- n_test_dataset:", n_test_dataset)
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

# {
# 	'obscene': {'accuracy': 0.9930735930735931, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0},
# 	'discriminatory': {'accuracy': 0.6735930735930736,
# 	'precision': 0.021108179419525065, 'recall': 0.5714285714285714, 'f1': 0.04071246819338423},
# 	'violent': {'accuracy': 0.9030303030303031, 'precision': 0.08411214953271028, 'recall': 0.391304347826087, 'f1': 0.13846153846153847},
# 	'illegal': {'accuracy': 0.9203463203463204, 'precision': 0.3146067415730337, 'recall': 0.4745762711864407, 'f1': 0.3783783783783784},
# 	'personal': {'accuracy': 0.8761904761904762, 'precision': 0.4514285714285714, 'recall': 0.626984126984127, 'f1': 0.5249169435215947},
# 	'corporate': {'accuracy': 0.754978354978355, 'precision': 0.287292817679558, 'recall': 0.8062015503875969, 'f1': 0.42362525458248473},
# 	'others': {'accuracy': 0.8761904761904762, 'precision': 0.7487046632124352, 'recall': 0.8626865671641791, 'f1': 0.8016643550624133}
# }


	print("Saving model to", args.output_dir)
	model.save_pretrained(args.output_dir)


if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
