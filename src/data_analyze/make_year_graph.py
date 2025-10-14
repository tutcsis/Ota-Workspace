import pandas as pd
import matplotlib.pyplot as plt
from tap import Tap

class Args(Tap):
  data_path: str = "tables/tweet_toxic_count.csv"
  # output_path: str = "year_graph.png"
  # output_path: str = "all_year_graph.png"
  output_path: str = "all_year_3toxic_graph.png"
  # categories: list = ['personal', 'others', 'illegal', 'corporate', 'violent', 'discriminatory', 'obscene']
  categories: list = ['obscene', 'violent', 'discriminatory']
  years: list = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]

def make_each_year_graph(args, df, year):
  new_df = df[df['year'] == year]
  plt.figure(figsize=(10, 6))
  for category in args.categories:
    plt.plot(new_df['month'], new_df[category]/new_df['total'], label=category, marker='o')
  
  plt.title(f'Toxic Tweet Ratio in {year}')
  plt.xlabel('Month')
  plt.ylabel('Ratio')
  plt.legend()
  plt.grid(True)
  plt.xticks(rotation=45)
  plt.tight_layout()
  plt.savefig('imgs/' + str(year) + args.output_path)


def main(args):
  df = pd.read_csv(args.data_path)
  df['year'] = pd.to_datetime(df['month'], format='%Y-%m').dt.year
  # for year in args.years:
    # make_each_year_graph(args, df, year)
    # new_df = df[df['year'] == year]
    # print(new_df.sum())
  yearly_df = df.groupby('year')[args.categories + ['total']].sum()
  yearly_df = yearly_df[(yearly_df.index >= 2012) & (yearly_df.index <= 2020)]
  # print(yearly_df)

  plt.figure(figsize=(10, 6))
  for category in args.categories:
    plt.plot(yearly_df.index, yearly_df[category]/yearly_df['total'], label=category, marker='o')
  
  plt.title(f'Toxic Tweet Ratio in 2012-2020')
  plt.xlabel('Year')
  plt.ylabel('Ratio')
  plt.legend()
  plt.grid(True)
  plt.xticks(rotation=45)
  plt.tight_layout()
  plt.savefig('imgs/' + args.output_path)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)

