import os
import json
from tap import Tap

class Args(Tap):
  retweet_ids_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/ja_retweet_ids/"
  tweet_ids_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/ja_tweet_ids/"
  only_retweets_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/ja_only_retweets.txt"
  common_ids_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/ja_common_ids.txt"

def get_directories(path: str):
  return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

def get_files(path: str):
  return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def read_ids_generator(file_path: str):
  with open(file_path, 'r') as f:
    for line in f:
      yield line.strip()

def process_tweet_files(base_path: str):
  tweet_ids = set()
  for file in get_files(base_path):
    file_path = os.path.join(base_path, file)
    for tweet_id in read_ids_generator(file_path):
      tweet_ids.add(tweet_id)
  return tweet_ids

def main(args):
  retweet_ids = process_tweet_files(args.retweet_ids_path)
  tweet_ids = process_tweet_files(args.tweet_ids_path)
  only_retweets = retweet_ids - tweet_ids
  common_ids = retweet_ids & tweet_ids
  with open(args.only_retweets_path, 'w') as f:
    for retweet_id in only_retweets:
      f.write(f"{retweet_id}\n")
  print(f"Only retweets saved to {args.only_retweets_path}")
  with open(args.common_ids_path, 'w') as f:
    for common_id in common_ids:
      f.write(f"{common_id}\n")
  print(f"Common IDs saved to {args.common_ids_path}")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
