# -*- python -*-
import gzip
import json
import random
import sys
from tap import Tap
from functools import partial
from pathlib import Path
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

class Args(Tap):
	srcfile: str = None
	srcdir: str = None
	output: str = None
	language: str = "ja"
	ratio: float = 0.001
	seed: int = 42
	num_processes: int = max(16, cpu_count())

def extract(srcfile):
	def openfile(filename):
		if str(filename).endswith(".gz"):
			return gzip.open(filename, 'rt', encoding="utf-8")
		else:
			return open(filename, 'r', encoding="utf-8")
	with openfile(srcfile) as f:
		for x in f:
			tid, body = x.split('\t', maxsplit=1)
			data = json.loads(body)
			if not data.get('id'):
				data['id'] = tid
			yield(data)

def language_filter(language, iterable):
	for x in iterable:
		lang = x.get('lang')
		if not lang:
			user = x.get('user')
			if user:
				lang = user.get('lang')
		if lang == language:
			yield(x)

def random_filter(ratio, iterable):
	for x in iterable:
		r = random.random()
		if r < ratio:
			yield x

def stream_sampling(srcfile, ratio, language):
	return random_filter(ratio, language_filter(language, extract(srcfile)))

def batch_sampling(srcfile, ratio, language):
	# multiprocessing を使って並列実行する場合，generator を返すことは
	# できない(generator は pickle できないため)．そのため，ここでは明
	# 示的に一旦全てのサンプルをメモリ上に蓄積してから返している．
	# 1に近い ratio を指定して実行すると，この段階で巨大なメモリを必要
	# として実行時エラーになるので要注意．
	return list(stream_sampling(srcfile, ratio, language))

def main(args):
	random.seed(args.seed)
	if args.output:
		dstfile = open(args.output, 'w', encoding="utf-8")
	else:
		dstfile = sys.stdout
	if args.srcfile:
		for x in stream_sampling(args.srcfile, args.ratio, args.language):
			print(json.dumps(x, ensure_ascii=False), file=dstfile)
	elif args.srcdir:
		files = sorted([x for x in Path(args.srcdir).iterdir() if x.is_file()])
		func = partial(batch_sampling, ratio=args.ratio, language=args.language)
		with Pool(processes=args.num_processes) as pool:
			for samples in tqdm(pool.imap(func, files), total=len(files), desc='Processing', disable=not args.output):
				for x in samples:
					print(json.dumps(x, ensure_ascii=False), file=dstfile)
	if args.output:
		dstfile.close()

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)