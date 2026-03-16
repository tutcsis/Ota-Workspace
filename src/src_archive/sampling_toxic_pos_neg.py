# 有害ラベルについて、正例・負例をサンプリング
from pathes import (
	TOXIC_MEDIA_TWEET_PATH,
	POS_NEG_ID_TABLE_PATH,
	SAMPLED_POS_NEG_TABLE_PATH,
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

class Args(Tap):
	toxic_data_folder: str = TOXIC_MEDIA_TWEET_PATH
	pos_neg_id_table_folder: str = POS_NEG_ID_TABLE_PATH
	sampled_toxic_table_folder: str = SAMPLED_POS_NEG_TABLE_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS
	sample_len: int = 50

def make_toxic_pos_neg_table(args):
	for file in tqdm(utils.get_file_names(args.toxic_data_folder)):
		pos_list = {toxic: [] for toxic in args.toxic_label}
		neg_list = {toxic: [] for toxic in args.toxic_label}
		month = file.split('.jsonl')[0]
		year = month.split('-')[0]
		if year not in args.years:
			continue

		with open(os.path.join(args.toxic_data_folder, file), 'r') as f:
			for id, line in enumerate(f):
				tw = json.loads(line)
				for toxic in args.toxic_label:
					label = f"{month},{id}"
					if toxic in tw and tw[toxic] == 1:
						pos_list[toxic].append(label)
					else:
						neg_list[toxic].append(label)

		for toxic in args.toxic_label:
			print(f"{toxic} - pos: {len(pos_list[toxic])}({pos_list[toxic][0]}), neg: {len(neg_list[toxic])}({neg_list[toxic][0]})")
			# save pos/neg id table
			with open(os.path.join(args.pos_neg_id_table_folder, f"{toxic}_pos.txt"), 'a') as f_pos:
				for label in pos_list[toxic]:
					f_pos.write(f"{label}\n")
			with open(os.path.join(args.pos_neg_id_table_folder, f"{toxic}_neg.txt"), 'a') as f_neg:
				for label in neg_list[toxic]:
					f_neg.write(f"{label}\n")

def sampling_toxic_pos_neg(args):
	sampled_pos = dict()
	sampled_neg = dict()
	for toxic in args.toxic_label:
		# make sampled pos/neg dict
		sampled_pos[toxic] = dict()
		sampled_neg[toxic] = dict()

		with open(os.path.join(args.pos_neg_id_table_folder, f"{toxic}_pos.txt"), 'r') as f_pos:
			pos_lines = [line.strip() for line in f_pos.readlines()]
			sampled_pos_toxic = sorted(random.sample(pos_lines, min(args.sample_len, len(pos_lines))))
			for sample in sampled_pos_toxic:
				month, index = sample.split(',')
				if month not in sampled_pos[toxic]:
					sampled_pos[toxic][month] = []
				sampled_pos[toxic][month].append(int(index))
		
		with open(os.path.join(args.pos_neg_id_table_folder, f"{toxic}_neg.txt"), 'r') as f_neg:
			neg_lines = [line.strip() for line in f_neg.readlines()]
			sampled_neg_toxic = sorted(random.sample(neg_lines, min(args.sample_len, len(neg_lines))))
			for sample in sampled_neg_toxic:
				month, index = sample.split(',')
				if month not in sampled_neg[toxic]:
					sampled_neg[toxic][month] = []
				sampled_neg[toxic][month].append(int(index))
		print(f"sampled pos {toxic}: {len(sampled_pos_toxic)}")
		print(f"sampled neg {toxic}: {len(sampled_neg_toxic)}")

		# get sampled pos/neg tweets text
		sampled_pos_texts = pd.DataFrame(columns=['month', 'index', 'text'])
		sampled_neg_texts = pd.DataFrame(columns=['month', 'index', 'text'])

		print(f"Sampling toxic label: {toxic}")
		pos_index = 0
		neg_index = 0

		for pos_key in sampled_pos[toxic].keys():
			with open(os.path.join(args.toxic_data_folder, f"{pos_key}.jsonl"), 'r') as f:
				for i, line in enumerate(f):
					if i in sampled_pos[toxic][pos_key]:
						tw = json.loads(line)
						sampled_pos_texts.loc[pos_index] = [pos_key, i, tw['text']]
						pos_index += 1
		print(sampled_pos_texts.head())
		sampled_pos_texts.to_csv(os.path.join(args.sampled_toxic_table_folder, f"{toxic}_pos.csv"), index=False)

		for neg_key in sampled_neg[toxic].keys():
			with open(os.path.join(args.toxic_data_folder, f"{neg_key}.jsonl"), 'r') as f:
				for i, line in enumerate(f):
					if i in sampled_neg[toxic][neg_key]:
						tw = json.loads(line)
						sampled_neg_texts.loc[neg_index] = [neg_key, i, tw['text']]
						neg_index += 1
		print(sampled_neg_texts.head())
		sampled_neg_texts.to_csv(os.path.join(args.sampled_toxic_table_folder, f"{toxic}_neg.csv"), index=False)

def main(args):
	print(f"toxic data folder path: {args.toxic_data_folder}")

	# init toxic pos/neg data list
	if not os.path.exists(os.path.join(args.pos_neg_id_table_folder, f"{args.toxic_label[0]}_pos.txt")):
		make_toxic_pos_neg_table(args)
	print("Finished making toxic pos/neg id table")

	# sampling toxic pos/neg data
	sampling_toxic_pos_neg(args)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
