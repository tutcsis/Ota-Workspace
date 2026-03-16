# tables/check_ja_tweets/ フォルダに月毎の集計結果を保存している
#  これらを結合して１つのcsvファイルにする

import utils
import os
from tap import Tap

class Args(Tap):
  month_table_folder: str = "/work/s245302/Ota-Workspace/tables/check_ja_tweets/"
  out_table: str = "/work/s245302/Ota-Workspace/tables/ja_tweet_check_results.csv"

def main(args):
  out_texts = []
  for file in utils.get_file_names(args.month_table_folder):
    month_path = os.path.join(args.month_table_folder, file)
    with open(month_path, 'r') as f:
      month_text = f.readline()
      out_texts.append(month_text)
  with open(args.out_table, 'w') as f:
    f.write(",gold_pos,gold_neg,pos_pos,pos_neg,neg_pos,neg_neg\n")
    for line in out_texts:
      f.write(line)

if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
