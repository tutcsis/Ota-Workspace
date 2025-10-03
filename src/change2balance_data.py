import os
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
  print("yes_dataset: ", yes_dataset.column_names)
  
  yes_dataset.to_json(args.yes_dataset_path, force_ascii=False)
  no_dataset.to_json(args.no_dataset_path, force_ascii=False)
  return yes_dataset, no_dataset

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
  # 3. split no_dataset -> no_train_dataset, no_test_dataset
  # 4. concatenate train_dataset, test_dataset

if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
