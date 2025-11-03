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
  0. その他

# 手順
1. 1ヶ月・ユーザ・ラベルごとに有害投稿数を記録する
  - 2012-2020年の各ファイルを見る
    - dataframe で２次元の表を作って、記録していく
  - 有害投稿データ保存場所： ``data/twitter_stream/1000-toxic-sampling-user_add/``
  - 各年度の有害投稿をしているユーザの表：``src/twitter_stream/tweets_group_analysis/tables/toxic_users/2012-11.csv`` など
  ```
  ,obscene,discriminatory,violent,all
  111111111,1,2,0,3
  222222222,1,1,0,2
  ..
  444444444,1,1,3,4
  ```

2. 1で作った全てのcsvファイルを確認して、各ユーザ・有害ラベルごとでグループ分けをする
  - グループ分けをした後の表：``src/twitter_stream/tweets_group_analysis/tables/grouped_toxic_user.csv``
  ```
    - yearly_users_df[toxic] に年度毎のカラムがあるため、そこにユーザ毎の有害投稿数を加算していく
    - 出来上がった yearly_users_df[toxic] をグループ分けの規則に従い0,1,2,3,4のいずれかをラベル付けする
    - それぞれのtoxicにおけるグループ名のみを一つのdataframe に保存する
  user_id,g_obscene,g_discriminatory,g_violent,g_all
  111111111,1,2,3,2
  222222222,2,2,4,1
  ..
  444444444,0,3,2,4
  ```

3. 1,2の表を結合して、月毎のユーザごとでグループと有害な投稿数を記録する
  - ユーザ別、月毎の有害投稿数とグループ：``src/twitter_stream/tweets_group_analysis/tables/grouped_toxic_users/2019-01.csv``
  ```
    - 2で作った、csvファイルをdataframeとして読み込む
    - 1で作った、それぞれの月のファイルをdataframeとして読み込む
    - 各toxicのgroup名を追記して書き出し
  user_id,obscene,discriminatory,violent,all,g_obscene,g_discriminatory,g_violent,g_all
  111111111,1,2,4,7,1,2,3,2
  222222222,2,1,1,3,2,2,4,1
  ..
  444444444,1,3,2,5,0,3,2,4
  ```

4. 3の表を使用して、月・グループ毎の有害投稿数を記録する
  - 月・グループ毎の有害投稿数： ``src/twitter_stream/tweets_group_analysis/tables/grouped_monthly_counts/obscene.csv`` など
    - 3で作った、csvファイルをdataframeとして読み込む
    - toxicごとに記録用のdataframeを作成する
    - それぞれのtoxicに対して、各ユーザの有害投稿数をその月のgroupの列に加算する
    - 最後に、全てのgroupの総和をallにする
  ```
  ,0,1,2,3,4,all
  2011-01,100,200,300,400,500,1500
  2011-02,200,400,500,500,100,1700
  ..
  2020-12,100,100,100,100,100,500
  ```
