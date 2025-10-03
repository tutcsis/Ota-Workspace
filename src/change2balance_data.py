import os
import numpy as np
from datasets import load_dataset, Dataset, concatenate_datasets
from tap import Tap

class Args(Tap):
  dataset_path: str = "data/llmjp_toxicity_dataset/toxicity_dataset_ver2.jsonl"
  columns = ["obscene", "discriminatory", "violent", "illegal", "personal", "corporate", "others"]
  base = ["id", "text", "label"]
  yes_samples: int = 4
  yes_dataset_path: str = "data/llmjp_toxicity_dataset/yes_dataset.jsonl"
  no_dataset_path: str = "data/llmjp_toxicity_dataset/no_dataset.jsonl"
  train_path: str = "data/llmjp_toxicity_dataset/train_dataset.jsonl"
  test_path: str = "data/llmjp_toxicity_dataset/test_dataset.jsonl"

def make_yes_no_datasets(args):
  dataset = load_dataset("json", data_files=args.dataset_path, split="train")
  dataset = dataset.add_column(name="flag", column=[0]*len(dataset))
  df = dataset.to_pandas()
  for category in args.columns:
    print("Check category Y/N: ", category)
    df.loc[df[category] == 'yes', 'flag'] = 1
  yes_df = df[df['flag'] == 1].drop(columns=['flag'])
  no_df = df[df['flag'] == 0].drop(columns=['flag'])
  yes_dataset = Dataset.from_pandas(yes_df).remove_columns(['__index_level_0__'])
  no_dataset = Dataset.from_pandas(no_df).remove_columns(['__index_level_0__'])
  # 出力がアスキーになるのを阻止  
  yes_dataset.to_json(args.yes_dataset_path, force_ascii=False)
  no_dataset.to_json(args.no_dataset_path, force_ascii=False)
  return yes_dataset, no_dataset

def split_yes_dataset(args, yes_dataset):
  yes_dataset = yes_dataset.add_column(name="flag", column=[0]*len(yes_dataset))
  yes_df = yes_dataset.to_pandas()
  for category in args.columns:
    print("split yes_dataset to train/test: ", category)
    yes_indices = set(yes_df[yes_df[category] == "yes"].index)
    flag_indices = set(yes_df[yes_df["flag"] == 1].index)
    diff_indices = list(yes_indices - flag_indices)
    # flag=0 の中で yes_samples の数だけランダムに選ぶ
    if diff_indices:
      selected_indices = np.random.choice(
        diff_indices,
        size=min(args.yes_samples, len(diff_indices)),
        replace=False
      )
      yes_df.loc[selected_indices, "flag"] = 1
  yes_train_df = yes_df[yes_df['flag'] == 1].drop(columns=['flag'])
  yes_test_df = yes_df[yes_df['flag'] == 0].drop(columns=['flag'])
  yes_train_dataset = Dataset.from_pandas(yes_train_df).remove_columns(['__index_level_0__'])
  yes_test_dataset = Dataset.from_pandas(yes_test_df).remove_columns(['__index_level_0__'])
  return yes_train_dataset, yes_test_dataset

def split_no_dataset(args, no_dataset, no_train_len):
  no_dataset = no_dataset.add_column(name="flag", column=[0]*len(no_dataset))
  no_df = no_dataset.to_pandas()
  no_indices = list(no_df[no_df["flag"] == 0].index)
  selected_indices = np.random.choice(
    range(no_dataset.num_rows),
    size=no_train_len,
    replace=False
  )
  no_df.loc[selected_indices, "flag"] = 1
  no_train_df = no_df[no_df['flag'] == 1].drop(columns=['flag'])
  no_test_df = no_df[no_df['flag'] == 0].drop(columns=['flag'])
  no_train_dataset = Dataset.from_pandas(no_train_df).remove_columns(['__index_level_0__'])
  no_test_dataset = Dataset.from_pandas(no_test_df).remove_columns(['__index_level_0__'])
  return no_train_dataset, no_test_dataset

def main(args):
  # 1. dataset -> yes_dataset, no_dataset
  if not os.path.exists(args.yes_dataset_path) or not os.path.exists(args.no_dataset_path):
    yes_dataset, no_dataset = make_yes_no_datasets(args)
  else:
    yes_dataset = load_dataset("json", data_files=args.yes_dataset_path, split="train")
    no_dataset = load_dataset("json", data_files=args.no_dataset_path, split="train")
  print("yes_dataset: ", yes_dataset)
  print("no_dataset: ", no_dataset)

  # 2. split yes_dataset -> yes_train_dataset, yes_test_dataset
  yes_train_dataset, yes_test_dataset = split_yes_dataset(args, yes_dataset)
  print("yes_train_dataset: ", yes_train_dataset)
  print("yes_test_dataset: ", yes_test_dataset)

  # 3. split no_dataset -> no_train_dataset, no_test_dataset
  no_train_dataset, no_test_dataset = split_no_dataset(args, no_dataset, no_train_len=yes_train_dataset.num_rows)
  print("no_train_dataset: ", no_train_dataset)
  print("no_test_dataset: ", no_test_dataset)
  
  # 4. concatenate train_dataset, test_dataset
  train_dataset = concatenate_datasets([yes_train_dataset, no_train_dataset])
  test_dataset = concatenate_datasets([yes_test_dataset, no_test_dataset])
  train_dataset.to_json(args.train_path, force_ascii=False)
  test_dataset.to_json(args.test_path, force_ascii=False)

if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
