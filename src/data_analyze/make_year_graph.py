import pandas as pd
import matplotlib.pyplot as plt
from tap import Tap

class Args(Tap):
  data_path: str = "tweet_toxic_count.csv"
  output_path: str = "year_graph.png"


def main(args):
  df = pd.read_csv(args.data_path)
  df['year'] = pd.to_datetime(df['month'], format='%Y-%m').dt.year
  for year in [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]:
    new_df = df[df['year'] == year]
    categories = ['personal', 'others', 'illegal', 'corporate', 'violent', 'discriminatory', 'obscene']
    plt.figure(figsize=(10, 6))
    for category in categories:
      plt.plot(new_df['month'], new_df[category]/new_df['total'], label=category, marker='o')
    
    plt.title(f'Toxic Tweet Ratio in {year}')
    plt.xlabel('Month')
    plt.ylabel('Ratio')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(str(year) + args.output_path)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

