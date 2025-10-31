import json
import random
from tap import Tap

class Args(Tap):
  sample_len: int = 1000
  data_path: str = ""
  # data_path: str = "data/twitter_stream/sample_ja/2020-01/2020-01-01-00.txt"
  out_path: str = ""
  # out_path: str = "data/twitter_stream/text_ja/2020-01/2020-01-01-00.json"
  # out_path: str = "data/twitter_stream/text_ja/2020-01/2020-01-01-00.txt"

def count_lines(path):
  count = 0
  with open(path, "r") as f:
    for _ in f:
      count += 1
  return count

def main(args):
  # generate random value between 0 and tweet_len
  print("data_path: ", args.data_path)
  print("out_path: ", args.out_path)
  tweet_len = count_lines(args.data_path)
  rand_idxs = random.sample(range(tweet_len), min(args.sample_len, tweet_len))
  tweet_dict = {}

  with open(args.data_path, "r") as f:
    for i, line in enumerate(f):
      if i in rand_idxs:
        tweet_id, json_str = line.strip().split("\t")
        data = json.loads(json_str)
        tweet_dict[tweet_id] = repr(data["text"])[1:-1]
  
  # with open(args.out_path, "w", encoding="utf-8") as f:
  #   for tweet_id, text in tweet_dict.items():
  #     f.write(f"{tweet_id}\t{text}\n")

  with open(args.out_path, "w", encoding="utf-8") as f:
    json.dump(tweet_dict, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
