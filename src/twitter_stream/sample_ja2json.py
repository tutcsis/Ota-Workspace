import random
import os
import json
import utils
from pathlib import Path
from tap import Tap
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class Args(Tap):
	dataset_path: str = ""
	output_path: str = ""
	month: str = ""

	# 0.1% sampling
	sampling_ratio: float = 0.001
	is_sample: bool = False

	twitter_machine_dict = {
		"Twitter for iPhone": "iphone",
		"Twitter for iPad": "ipad",
		"Twitter for Android": "android",
		"Twitter for Android Tablets": "androidtablet",
		"Twitter Web Client": "web"
	}
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

def check_extended_entities(month):
	curr_year, curr_month = month.split('-')
	if int(curr_year) < 2014 or (int(curr_year) == 2014 and int(curr_month) <= 8):
		return "entities"	# before September 2014
	else:
		return "extended_entities" # after October 2014

def labeling_machine(args, user_machine, host_name):
	if host_name not in args.tw_hosts:
		return "other"
	for key in args.twitter_machine_dict.keys():
		if key in user_machine:
			return args.twitter_machine_dict[key]
	return "other"

def get_json_info(file_path):
	samples = []
	with open(file_path, 'r', encoding='utf-8') as f:
		for i, line in enumerate(f):
			# 1% sampling
			if args.is_sample:
				curr_r = random.random()
				if curr_r < args.sampling_ratio:
					continue

			# get tweet json
			if "\t" in line:
				tweet_id, json_str = line.strip().split("\t")
				json_data = json.loads(json_str)
			else:
				json_data = json.loads(line.strip())
				tweet_id = str(json_data.get("id"))

			# media information
			media = json_data.get(check_extended_entities(args.month), {}).get("media", [])
			urls = json_data.get("entities", {}).get("urls", [])

			# machine information
			soup = BeautifulSoup(json_data.get("source", ""), "html.parser")
			user_machine = soup.get_text().strip()
			if user_machine is None:
				user_machine = ""
			href_value = soup.a['href'] if soup.a else ""
			host_name = urlparse(href_value).hostname if href_value else ""
			machine_label = labeling_machine(args, user_machine, host_name)

			samples.append({
				"tweet_id": tweet_id,
				"text": repr(json_data["text"])[1:-1],
				"user_id": json_data["user"]["id"],
				"screen_name": json_data["user"]["screen_name"],
				# "time": file.split('.txt')[0],
				"month": args.month,
				"media": media,
				"urls": urls,
				"user_machine": user_machine,
				"host_name": host_name,
				"machine_label": machine_label,
			})
	return samples

def main(args):
	print(f"dataset_path: {args.dataset_path}, output_path: {args.output_path}, month: {args.month}")
	samples = []
	if os.path.isfile(args.dataset_path):
		samples = get_json_info(args.dataset_path)
	else:
		for file in tqdm(utils.get_file_names(args.dataset_path)):
			file_path = os.path.join(args.dataset_path, file)
			samples.extend(get_json_info(file_path))

	output_file = os.path.join(args.output_path, f"{args.month}.jsonl")
	with open(output_file, 'w', encoding='utf-8') as outf:
		for sample in samples:
			outf.write(json.dumps(sample, ensure_ascii=False) + '\n')
	print(f"Saved {len(samples)} samples to {output_file}")

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

