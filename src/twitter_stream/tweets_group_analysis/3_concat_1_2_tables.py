from pathes import TOXIC_TWEET_PATH, USER_TOXIC_COUNTS_PATH,TOXIC_LABEL, USE_YEARS
import utils
import os
import json
import pandas as pd
from tap import Tap
from tqdm import tqdm
from collections import Counter

class Args(Tap):
	file_path: str = ""
	table_path: str = ""
	# input_path: str = TOXIC_TWEET_PATH
	toxic_label: list = TOXIC_LABEL
	years: list = USE_YEARS

def main(args):


if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

