import json
import random
from tap import Tap

class Args(Tap):
  sample_len: int = 100
  data_path: str = "data/twitter_stream/sample_ja/2020-01/2020-01-01-00.txt"

def count_lines(path):
  count = 0
  with open(path, "r") as f:
    for _ in f:
      count += 1
  return count

def main(args):
  # generate random value between 0 and tweet_len
  tweet_len = count_lines(args.data_path)
  rand_idxs = random.sample(range(tweet_len), args.sample_len)
  print(rand_idxs)
  tweet_dict = {}

  with open(args.data_path, "r") as f:
    for i, line in enumerate(f):
      if i in rand_idxs:
        tweet_id, json_str = line.strip().split("\t")
        data = json.loads(json_str)
        tweet_dict[i] = (tweet_id, data["text"])
  
  print(tweet_dict)



if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
