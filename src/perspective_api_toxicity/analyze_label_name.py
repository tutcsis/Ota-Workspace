import json
from tap import Tap

class Args(Tap):
  data_path: str = "data/toxicity"
  data_file_len: int = 7
  

def main(args):
  def file_name(i):
    return f"final_part_{i}.jsonl"

  # example: {"tweet_id":"1212160746164932609","identity_attack":0.00012544586,"profanity":0.008213009,"toxicity":0.0006754258,"insult":0.004864735,"threat":0.0053011146,"severe_toxicity":0.0000834465}
  for i in range(1, args.data_file_len + 1):
    with open(f"{args.data_path}/{file_name(i)}", "r") as f:
      label_names = set()
      for line in f:
        data = json.loads(line)
        for key in data.keys():
          if key not in "tweet_id":
            label_names.add(key)
    print(i, label_names)


if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
