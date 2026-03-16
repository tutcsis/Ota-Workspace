import pandas as pd
from tap import Tap

class Args(Tap):
	left_table_path: str = 'tables/1000tweet_toxic_count.csv'
	right_table_path: str = 'tables/ja_tweet_counts.csv'
	output_path: str = 'tables/merged_toxic_count_with_all_tweets.csv'
	concat_column: str = 'month'

def main(args):
	left_df = pd.read_csv(args.left_table_path)
	right_df = pd.read_csv(args.right_table_path)
	merged_df = pd.merge(left_df, right_df, on=args.concat_column, how='left')
	merged_df.to_csv(args.output_path, index=False)

if __name__ == "__main__":
	args = Args().parse_args()
	main(args)
