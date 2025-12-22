# 有害ラベル付きツイートに端末情報を追加
from pathes import (
	TOXIC_LABEL,
	USE_YEARS
)
import utils
import os
import json
import numpy as np
import pandas as pd
import random
from tap import Tap
from tqdm import tqdm
from collections import Counter
from bs4 import BeautifulSoup

class Args(Tap):
	# toxic_tweets: str = "/work/s245302/Ota-Workspace/data/twitter_stream/1000-toxic-sampling-user_add/"
	# all_data_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/"
	# output_tweets: str = "/work/s245302/Ota-Workspace/data/twitter_stream/1000-toxic-sampling-machine_add/"
	# month: str = "2011-10"
	toxic_tweets: str = ""
	all_data_path: str = ""
	output_tweets: str = ""
	month: str = ""
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS

def check_extended_entities(month):
	curr_year, curr_month = month.split('-')
	if int(curr_year) < 2014 or (int(curr_year) == 2014 and int(curr_month) <= 8):
		return "entities"	# before September 2014
	else:
		return "extended_entities" # after October 2014

def main(args):
	print(f"toxic_tweets: {args.toxic_tweets}, month: {args.month}")

	# setting
	tweet_dict = dict()
	added_tweet_list = list()

	print("Loading toxic tweets...")
	with open(f"{args.toxic_tweets}{args.month}.jsonl", 'r', encoding='utf-8') as f:
		for line in f:
			json_str = line.strip()
			json_data = json.loads(json_str)
			tw_time = json_data.get("time", "")
			if tweet_dict.get(tw_time, None) is None:
				tweet_dict[tw_time] = dict()
			tweet_dict[tw_time][json_data.get("tweet_id")] = json_data

	print("Adding user machine info...")
	for tw_time in tweet_dict.keys():
		with open(f"{args.all_data_path}{args.month}/{tw_time}.txt", 'r', encoding='utf-8') as f:
			for line in f:
				tweet_id, json_str = line.strip().split("\t")
				if tweet_dict[tw_time].get(tweet_id, None) is None:
					continue
				json_data = json.loads(json_str)
				media = json_data.get(check_extended_entities(args.month), {}).get("media", [])
				urls = json_data.get("entities", {}).get("urls", [])
				user_machine = BeautifulSoup(json_data.get("source", ""), "html.parser").get_text()
				tweet_dict[tw_time][tweet_id]["user_machine"] = user_machine
				tweet_dict[tw_time][tweet_id]["media"] = media
				tweet_dict[tw_time][tweet_id]["urls"] = urls
				added_tweet_list.append(tweet_dict[tw_time][tweet_id])

	print(f"Saving tweets with user machine info to {args.output_tweets}{args.month}.jsonl ...")
	with open(f"{args.output_tweets}{args.month}.jsonl", 'w', encoding='utf-8') as f:
		for tweet_data in added_tweet_list:
			f.write(json.dumps(tweet_data, ensure_ascii=False) + "\n")

	# print(tweet_dict["2011-10-10-23"])

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
