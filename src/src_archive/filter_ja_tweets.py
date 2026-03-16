import json
from tap import Tap

class Args(Tap):
	ja1_file: str = ""
	ja2_file: str = ""

def main(args):
  out_list = []
  with open(args.ja1_file, 'r', encoding='utf-8') as f:
    for line in f:
      tweet_id, json_str = line.strip().split("\t")
      json_data = json.loads(json_str)
      lang = json_data.get('lang', '')
      if not lang:
        lang = json_data.get('user', {}).get('lang', '')
      if lang == 'ja':
        out_list.append(line)

    with open(args.ja2_file, 'w') as of:
      for out_line in out_list:
        of.write(out_line)

if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
