import pandas as pd

# CSVファイルを読み込む
toxic_df = pd.read_csv('tables/1000tweet_toxic_count.csv')
ja_tweets_df = pd.read_csv('tables/ja_tweet_counts.csv')

# month列をキーにして結合する
merged_df = pd.merge(toxic_df, ja_tweets_df, on='month', how='left')

# 結果を新しいCSVファイルに保存
merged_df.to_csv('tables/merged_toxic_count_with_all_tweets.csv', index=False)
