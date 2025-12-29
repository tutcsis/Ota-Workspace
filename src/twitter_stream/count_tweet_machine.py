# ツイートを端末ごとに分類
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
	input_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/1000-toxic-sampling-machine_add/"
	# input_path: str = "/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/2012-10/"
	# machine_list: str = "/work/s245302/Ota-Workspace/tables/machine_counts.txt"
	machine_list: str = "/work/s245302/Ota-Workspace/tables/twitter_machine_counts.txt"
	host_list: str = "/work/s245302/Ota-Workspace/tables/host_counts.txt"
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	sample_len: int = 1000
	tw_hosts: list = [
		"twitter.com",
		"mobile.twitter.com"
		"about.twitter.com"
		"www.twitter.com"
		"dev.twitter.com"
		"apps.twitter.com"
	]

def count_lines(path):
	count = 0
	with open(path, "r") as f:
		for _ in f:
			count += 1
	return count

def count_tweet_machine(json_data):
	print(f"input_path: {args.input_path}")
	machine_counter = Counter()
	for file in utils.get_file_names(args.input_path):
		month = file.split('.jsonl')[0]
		year = month.split('-')[0]
		print(f"month: {month}")
		if year not in args.years:
			continue

		file_path = os.path.join(args.input_path, file)
		with open(file_path, 'r', encoding='utf-8') as f:
			for line in f:
				json_data = json.loads(line.strip())
				user_host = json_data.get("host_name", "Unknown")
				user_machine = json_data.get("user_machine", "Unknown").rstrip()
				if user_machine == "":
					user_machine = "Unknown"
				if user_host in args.tw_hosts:
					machine_counter[user_machine] += 1

	# output machine counts
	with open(args.machine_list, "w", encoding="utf-8") as f_out:
		for machine, count in machine_counter.items():
			f_out.write(f"{machine}\t{count}\n")

def count_tweet_host(json_data):
	print(f"input_path: {args.input_path}")
	host_counter = Counter()
	for file in utils.get_file_names(args.input_path):
		month = file.split('.jsonl')[0]
		year = month.split('-')[0]
		print(f"month: {month}")
		if year not in args.years:
			continue

		file_path = os.path.join(args.input_path, file)
		with open(file_path, 'r', encoding='utf-8') as f:
			for line in f:
				json_data = json.loads(line.strip())
				user_host = json_data.get("host_name", "Unknown")
				if user_host == "":
					user_host = "Unknown"
				host_counter[user_host] += 1

	# output host counts
	with open(args.host_list, "w", encoding="utf-8") as f_out:
		for host, count in host_counter.items():
			f_out.write(f"{host}\t{count}\n")

def main(args):
	if not os.path.exists(args.machine_list):
		count_tweet_machine(json)

	if not os.path.exists(args.host_list):
		count_tweet_host(json)

	# load machine counts
	machine_counts = {}
	with open(args.machine_list, "r", encoding="utf-8") as f:
		for line in f:
			# print(line)
			machine, count = line.strip().split("\t")
			machine_counts[machine] = int(count)

	sorted_machines = sorted(machine_counts.items(), key=lambda x: x[1], reverse=True)
	total_count = sum(machine_counts.values())
	i = 1
	print("rank,machine,count")
	for machine, count in sorted_machines:
		if i == 10:
			break
		# if count < 100:
		# 	continue
		# if machine.startswith("Twitter"):
		# 	print(f"{i},{machine},{count}")
		print(f"{i},{machine},{count}")
		i += 1

	# load host counts
	host_counts = {}
	with open(args.host_list, "r", encoding="utf-8") as f:
		for line in f:
			# print(line)
			host, count = line.strip().split("\t")
			host_counts[host] = int(count)

	sorted_hosts = sorted(host_counts.items(), key=lambda x: x[1], reverse=True)
	total_host_count = sum(host_counts.values())
	i = 1
	# print("rank,host,count")
	for host, count in sorted_hosts:
		# if i == 50:
		# 	break
		# if count < 100:
		# 	continue
		# if ".twitter.com" in host:
		# 	print(f"{i},{host},{count}")
		i += 1

		# tweet_len = count_lines(file_path)
		# sample_keys = random.sample(range(tweet_len), min(args.sample_len, tweet_len))
		# print(sample_keys)
		# with open(file_path, 'r', encoding='utf-8') as f:
		# 	for i, line in enumerate(f):
		# 		if i in sample_keys:
		# 			tweet_id, json_str = line.strip().split("\t")
		# 			json_data = json.loads(json_str)
		# 			user_machine = BeautifulSoup(json_data.get("source", ""), "html.parser").get_text()
		# 			print(user_machine)
		# break

	print(f"Total tweet count: {total_count}")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
