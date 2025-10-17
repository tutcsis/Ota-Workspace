import os
import json
from tap import Tap

class Args(Tap):
  input_path: str = ""
  retweet_ids_path: str = ""
  tweet_ids_path: str = ""
  # input_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja"
  # retweet_ids_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/ja_retweet_ids"
  # tweet_ids_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/ja_tweeted_ids"
  month: str = ""

def get_directories(path: str):
  return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

def get_files(path: str):
  return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def main(args):
  retweeted_ids = set()
  tweet_ids = []
  files = get_files(args.input_path)
  for file in files:
    with open(os.path.join(args.input_path, file), 'r') as f:
      for line in f:
        tweet_id, json_text = line.strip().split('\t')
        tweet_ids.append(tweet_id)
        tweet = json.loads(json_text)
        if 'retweeted_status' in tweet:
          retweeted_ids.add(tweet['retweeted_status']['id'])
  print(f"Total unique retweeted IDs: {len(retweeted_ids)}")
  with open(os.path.join(args.retweet_ids_path, f'{args.month}.txt'), 'w') as f:
    for retweet_id in retweeted_ids:
      f.write(f"{retweet_id}\n")
  print(f"Total tweet IDs: {len(tweet_ids)}")
  with open(os.path.join(args.tweet_ids_path, f'{args.month}.txt'), 'w') as f:
    for tweet_id in tweet_ids:
      f.write(f"{tweet_id}\n")
  print(f"Retweeted IDs saved to {args.retweet_ids_path}")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
