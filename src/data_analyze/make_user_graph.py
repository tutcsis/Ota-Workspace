import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tap import Tap

class Args(Tap):
  # file pathes
  table_path: str = "tables/1000_toxic_user_count.csv"
  graph_path: str = "imgs/1000tweets_toxic_user_count.png"

  user_years: list = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]

  graph_labels: list = ["obscene", "discriminatory", "violent"]
  # graph_labels: list = ["toxic_user_count"]
  graph_title: str = "Toxic User Count"
  graph_xlabel: str = "month"
  graph_ylabel: str = "users"

def main(args):
  df = pd.read_csv(args.table_path, index_col=0)
  df = df[df.index.str.split('-').str[0].isin(args.user_years)]
  # 欠損月を0埋め
  for year in args.user_years:
    for month in range(1, 12+1):
      id = f"{year}-{str(month).zfill(2)}"
      if id not in df.index:
        df.loc[id] = [0 for _ in range(len(df.columns))]
        print('Added id: ', id)
  df = df.sort_index()
  print("id: ", list(df.index))

  plt.figure(figsize=(10, 6))
  for label in args.graph_labels:
    plt.plot(df.index, df[label], label=label, marker='o')
  # グリッドの名前を年に変更
  plt.xticks(np.linspace(0, 12*len(args.user_years), len(args.user_years)+1), args.user_years + [""])
  plt.title(args.graph_title)
  plt.xlabel(args.graph_xlabel)
  plt.ylabel(args.graph_ylabel)
  plt.legend()
  plt.grid(True)
  plt.tight_layout()
  plt.savefig(args.graph_path)
  for tick, label in zip(plt.gca().get_xticks(), plt.gca().get_xticklabels()):
    print("{:5.2f}: '{}'".format(tick, label.get_text()))


if __name__ == "__main__":
  args = Args().parse_args()
  main(args)
