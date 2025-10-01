from datasets import load_dataset
from transformers import (
	AutoTokenizer,
	AutoModel,
	AutoModelForSequenceClassification,
	BitsAndBytesConfig,
	DataCollatorWithPadding,
	Trainer,
	TrainingArguments,
)
from transformers.modeling_outputs import (
	SequenceClassifierOutput,
)
from peft import (
	LoraConfig,
	get_peft_model,
	prepare_model_for_kbit_training,
	TaskType
)
from sklearn.metrics import accuracy_score, mean_squared_error
import numpy as np
import torch

import json
from datetime import datetime
from pathlib import Path
from tap import Tap
from typing import Literal


class Args(Tap):
	dataset_path: str = "data/llmjp_toxicity_dataset/toxicity_dataset_ver2.jsonl"
	dataset_version: Literal["ver1", "ver2"] = "ver2"
	key_label: Literal["writer", "reader1", "reader2", "reader3", "avg_readers"] = "avg_readers"
	num_labels: int = 2
	max_length: int = 1024

	model_name: str = "llm-jp/llm-jp-3-1.8b"
	output_dir: str = ""

	num_epochs: int = 1
	batch_size: int = 8
	per_device_batch_size: int = 8

	learning_rate: float = 1e-4
	weight_decay: float = 0.01
	warmup_ratio: float = 0.2
	lora_rank: int = 16
	lora_dropout: float = 0.05

	debug: bool = False
	use_bf16: bool = False # torch.cuda.is_bf16_supported() is unreliable.
	use_fp16: bool = False

	@property
	def torch_dtype(self):
		if self.use_bf16:
			return torch.bfloat16
		elif self.use_fp16:
			return torch.float16
		else:
			return torch.float32

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
		print(json.dumps({
			"dataset_path": self.dataset_path,
			"dataset_version": self.dataset_version,
			"key_label": self.key_label,
			"model_name": self.model_name
		}), file=self.log_file )

	def training_args(self):
		x = TrainingArguments(
			output_dir=self.output_dir,
			per_device_train_batch_size=self.per_device_batch_size,
			per_device_eval_batch_size=self.per_device_batch_size,
			gradient_accumulation_steps=self.batch_size // self.per_device_batch_size,
			num_train_epochs=self.num_epochs,
			eval_strategy="epoch",
			save_strategy="epoch",
			optim="adamw_torch",
			learning_rate=self.learning_rate,
			weight_decay=self.weight_decay,
			lr_scheduler_type="inverse_sqrt",
			warmup_ratio=self.warmup_ratio,
			bf16=self.use_bf16,
			fp16=self.use_fp16,
			load_best_model_at_end=True,
		)
		print(json.dumps(x.to_dict()), file=self.log_file)
		return x

	def peft_config(self):
		x = LoraConfig(
			r=self.lora_rank,
			lora_alpha=self.lora_rank * 2,
			lora_dropout=self.lora_dropout,
			inference_mode=False,
			target_modules="all-linear",
		)
		print(json.dumps(x.to_dict()), file=self.log_file)
		return x


# https://zenn.dev/kitchy/articles/8282928b398cc7 is another implementation example using torch.nn.ModuleDict.
class MultiTaskClassifier(torch.nn.Module):
	def __init__(self, encoder, num_labels, tasknames, bias=False, dtype=None):
		super().__init__()
		self.tasknames = tasknames
		self.add_module("encoder", encoder)
		self.add_module("head", torch.nn.ModuleDict())
		for taskname in tasknames:
			self.head[taskname] = torch.nn.Linear(
				encoder.config.hidden_size,
				num_labels,
				bias=bias,
				dtype=dtype)
		self.loss_fn = torch.nn.CrossEntropyLoss()

	def forward(self, input_ids, attention_mask, labels):
		outputs = self.encoder(
			input_ids=input_ids,
			attention_mask=attention_mask,
		)
		seq_length = attention_mask.sum(dim=1)
		eos_hidden_states = outputs.last_hidden_state[
			torch.arange(
				seq_length.size(0),
				device=outputs.last_hidden_state.device,
			),
			seq_length - 1,
		]

		logits = []
		for taskname in self.tasknames:
			logits.append(self.head[taskname](eos_hidden_states))
		logits = torch.stack(logits, dim=1)
		# The shepe of `logits' must be (batch_size, len(tasknames), num_labels).
		_logits = logits.reshape((-1, logits.shape[2]))
		# Its shape is converted to (batch_size * len(tasknames), num_labels).

		# The shape of original `labels' must be (batch_size, len(tasknames)).
		_labels = labels.reshape((-1,))
		# Its shape is converted to (batch_size * len(tasknames)).

		loss = self.loss_fn(_logits, _labels)
		return SequenceClassifierOutput(
			loss=loss,
			logits=logits,
		)


def main(args):
	tokenizer = AutoTokenizer.from_pretrained(args.model_name)

	dataset = load_dataset("json", data_file=args.dataset_path, split="train")
	tasknames = list(dataset["train"].features[args.key_label].keys())
	if args.debug:
		for split in dataset.keys():
			dataset[split] = dataset[split].select(range(len(dataset[split]) // 100))

	# The following copy of string is necesssary to avoid the Pickle warnings.
	keylabel = args.key_label[:]
	def preprocess_function(examples):
		tokenized = tokenizer(examples["sentence"], truncation=True)
		tokenized["label"] = [[x[k]+2 if k == "sentiment" else x[k] for k in tasknames] for x in examples[keylabel]]
		return tokenized
	tokenized_dataset = dataset.map(preprocess_function, batched=True)
	#print(dataset["train"][-3:])
	#print(tokenized_dataset["train"][-3:])
	data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

	def compute_metrics(eval_pred):
		predictions, labels = eval_pred
		# The shape of `predictions` is (number of test instances, number of tasks, number of labels)
		# The shape of `labels` is (number of test instances, number of tasks)
		metrics = {}
		for i,taskname in enumerate(tasknames):
			_predictions = np.argmax(predictions[:,i], axis=1)
			_labels = labels[:,i]
			metrics[taskname] = {
				"accuracy": accuracy_score(_labels, _predictions),
				"mse": mean_squared_error(_labels, _predictions)
			}
		return metrics

	# https://huggingface.co/docs/peft/developer_guides/quantization
	quantization_config = BitsAndBytesConfig(
		load_in_4bit=True,
		bnb_4bit_quant_type="nf4",
		bnb_4bit_use_double_quant=True,
		bnb_4bit_compute_dtype=args.torch_dtype,
	)
	model = AutoModel.from_pretrained(
		args.model_name,
		device_map="auto",
		torch_dtype=args.torch_dtype,
		trust_remote_code=True,
		quantization_config=quantization_config,
	)
	print(f"Loaded model uses {model.get_memory_footprint()} bytes")
	model = prepare_model_for_kbit_training(model)
	model = get_peft_model(model, args.peft_config())
	model.print_trainable_parameters()
	model = MultiTaskClassifier(model, args.num_labels, tasknames, dtype=args.torch_dtype)

	trainer = Trainer(
		model=model,
		args=args.training_args(),
		train_dataset=tokenized_dataset["train"],
		eval_dataset=tokenized_dataset["test"],
		processing_class=tokenizer,
		data_collator=data_collator,
		compute_metrics=compute_metrics,
	)

	train_result = trainer.train()
	trainer.save_metrics("train", train_result.metrics)
	trainer.save_metrics("eval", trainer.evaluate())
	trainer.save_model(args.output_dir)
	tokenizer.save_pretrained(args.output_dir)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)