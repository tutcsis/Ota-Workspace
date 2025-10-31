# 目的
- twitter-stream 上の日本語の投稿に有害ラベルを付与させて、有害な投稿数を時系列でグラフにした
![有害投稿数](/imgs/1000tweets_2012-2020_3toxic.png)
- グラフを見ると、有害な投稿数が時系列でそれほど変化していない(一部全体の投稿数が多い時期はそれに合わせて有害投稿数も増加している)
- そこで、この有害な投稿数をユーザごとに分割して時系列で変化があるかを確かめたい。

# 実験要件
- グループ分け：有害な投稿をしていた時期で分ける
  1. 古参勢：2012-2020年
  2. 古参離脱勢：2012-2014年
  3. 中期離脱勢：2015-2017年
  4. 新規勢：2018-2020年
  5. その他

# 手順
1. 年度ごとで有害な投稿をしているユーザを記録
  - 2012-2020年の各ファイルを見る
  - 有害投稿データ保存場所： ``data/twitter_stream/1000-toxic-sampling-user_add/``
  - 各年度の有害投稿をしているユーザの表：``src/twitter_stream/tweets_group_analysis/tables/2012_toxic_users.csv`` など
  ```
  user_id,obscene,discriminatory,violent,all
  111111111,1,1,0,1
  111111111,1,1,0,1
  ..
  111111111,1,1,0,1
  ```

2. 1で作った全てのcsvファイルを確認して、各ユーザ・有害ラベルごとでグループ分けをする
  - グループ分けをした後の表：``src/twitter_stream/tweets_group_analysis/tables/grouped_toxic_user.csv``
  ```
  user_id,obscene,discriminatory,violent,all
  111111111,1,2,4,3
  111111112,2,1,1,2
  ..
  111111113,1,3,2,4
  ```

3. 1ヶ月・ユーザ・ラベルごとに有害投稿数を記録する
  - ユーザ別、月毎の有害投稿数：``src/twitter_stream/tweets_group_analysis/tables/toxic_counts/2019-01.csv`` など
  ```
  user_id,obscene,discriminatory,violent,all
  111111111,1,2,4,7
  111111112,2,1,1,3
  ..
  111111113,1,3,2,5
  ```

4. 2,3の表を結合して、月毎のユーザごとでグループと有害な投稿数を記録する
  - ユーザ別、月毎の有害投稿数とグループ：``src/twitter_stream/tweets_group_analysis/tables/grouped_toxic_counts/2019-01.csv``
  ```
  user_id,obscene,discriminatory,violent,all,group
  111111111,1,2,4,7,1
  111111112,2,1,1,3,2
  ..
  111111113,1,3,2,5,5
  ```

5. 4の表を使用して、月・グループ毎の有害ユーザ数を記録する
  - 月・グループ毎の有害ユーザ数：``src/twitter_stream/tweets_group_analysis/tables/obscene_group_counts.csv``, ``src/twitter_stream/tweets_group_analysis/tables/discriminatory_group_counts.csv``, ``src/twitter_stream/tweets_group_analysis/tables/violent_group_counts.csv``, ``src/twitter_stream/tweets_group_analysis/tables/all_group_counts.csv``
  ```
  ,1,2,3,4,5,all
  2011-01,100,200,300,400,500,1500
  2011-02,200,400,500,500,100,1700
  ..
  2020-12,100,100,100,100,100,500
  ```
