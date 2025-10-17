# Ota-Workspace
とりあえず、実行したコードや試したいデータの置き場。あとで別のリポジトリに移動する

## llmjp-toxicity-dataset v2 をできるだけ均衡データに近づける
- 使用するデータセットは各ラベルについて全体に対する有害なデータの割合がとても少ない(不均衡データ)。
- 目的: そこで、有害でないデータをランダムで選択して削ったデータセットを用意する
- change2balance_data.py
1. 使用するデータセットを次の２つに分割
  - flag を用意して、あるラベルが Yes なら、flag を 1 にする。
  - すべてのラベルの探索が終わった後に flag の値で dataset を分ける
  - 「あるラベルが Yes であるデータ群」(yes_dataset)
  - 「すべてのラベルが No であるデータ群」(no_dataset)に分ける
2. yes_dataset の分割
  - yes_train_dataset: 各ラベルの Yes のデータが 4 個になるようにランダムサンプリングで集める
    - yes_indices: あるラベルの値が Yes である行番号
    - flag_indices: flag の値が Yes である行番号
    - ラベルの値が Yes で flag の値が No であるデータを集めたい
  - yes_test_dataset: yes_train_dataset 以外の yes_dataset のデータ
3. no_dataset の分割
  - no_train_dataset: yes_train_dataset の個数だけランダムサンプリングで収集
  - no_test_dataset: no_train_dataset 以外の no_dataset のデータ
4. 学習データとテストデータの生成
  - train_dataset: yes_train_dataset + no_train_dataset
  - test_dataset: yes_test_dataset + no_test_dataset

## setfitモデルによるツイートへの有害ラベルの付与
1. 学内の計算機にあるツイートデータをこのリポジトリにコピーする
  - `/work/my016/mirror/twitter-stream/{month}/{file}.txt` -> `/work/s245302/Ota-Workspace/data/twitter_stream/{month}/{file}.txt`
  - `copy_all_twitter_stream.sh`: `DATA_PATH` から月毎のフォルダ名を取得して、各フォルダ名を `copy_month_twitter_stream.sh` に渡してジョブとして実行している。
  - `copy_month_twitter_stream.sh`: `copy_all_twitter_stream.sh` から受け取ったある月のフォルダ名の直下にあるファイルを全て `OUTPUT_PATH` にコピーする。ファイルの回答は `gunzip` コマンドを使用
2. コピーしたツイートから日本語ツイートのみを抽出する
  - `twitter_stream/sample-archive-twitterstream/{month}/{file}.txt` -> `twitter_stream/sample-archive_ja/{month}/{file}.txt`
  - `filter_all_ja_tweet.sh`: `ARCHIVE_PATH`, `OUTPUT_PATH`, `month` を `filter_month_ja_tweet.sh` に渡す。
  - `filter_month_ja_tweet.sh`: `month` フォルダ直下のテキストファイルを全て取得して、lang="ja"が一つだけの行を抽出する。

3. jsonデータからtextラベルのみを取り出す
  - `twitter_stream/sample-archive_ja/{month}/{file}.txt` -> `twitter_stream/text-archive_ja/{month}/{file}.json`
  - `get_all_ja_tweet_text.sh`: `INPUT_PATH`, `OUTPUT_PATH`, `month` を `get_month_ja_tweet_text.sh` に渡す。
  - `get_month_ja_tweet_text.sh`: `month` フォルダ直下のファイルを `src/twitter_stream/get_tweet.py` に渡す。
  - `src/twitter_stream/get_tweet.py`: テキストファイルから取得した、ツイート情報を表す json データから text ラベルを取り出し、tweet_id とのペアを作成する。これらをまとめて `json` ファイルとして出力する。

4. 日本語ツイートの個数が多いので、１時間ごとに100件取得してそれを月毎に一つのファイルにまとめる
  - `twitter_stream/text-archive_ja/{month}/{file}.json` -> `twitter_stream/text-archive_ja/sampling/{month}.jsonl`
  - `sample_ja_tweet.sh`: `INPUT_PATH`, `OUTPUT_PATH`, `month` を `src/twitter_stream/sample_100_tweet.py` に渡す。
  - `sample_100_tweet.py`: `random.sample()` を使用して、ランダムで100件取得する。`tweet_id`, `text`, `time`, `month` からなる dict() を list に格納して `jsonl` ファイルとして出力する

5. 月毎の日本語ツイートに対して、setfitモデルを使用して7つの有害ラベルを付与する
  - `twitter_stream/text-archive_ja/sampling` -> `twitter_stream/toxic-archive_ja/sampling/`
  - `set_all_toxic_label.sh`: `INPUT_PATH`, `OUTPUT_PATH`, `month` を `set_month_toxic_label.sh` に渡す。
  - `set_month_toxic_label.sh`: 
6. 月毎で有害ラベルを計測する
  

3-a. 1時間ごとのtxtファイルからランダムで1000件jsonデータをし取得する
  - `twitter_stream/sample-archive_ja/{month}/{file}.txt` -> `twitter_stream/1000-sampling/{month}.json`
  - `sample_1000_all_tweets.sh`: `INPUT_PATH`, `OUTPUT_PATH`, `month` を `src/twitter_stream/sample_hour1000_tweets.py` に渡す。
  - `sample_hour1000_tweets.py`: `random.sample()` を使用して、ランダムで取得する予定の1000件を決定する。その後、その1000件を取得して、`tweet_id`, `text`, `time`, `month` からなる dict() を list に格納して `jsonl` ファイルとして出力する。

### リツイートしたツイートの元ツイートの格納先の特定
- retweeted_status があるツイートはリツイートであることが分かっている。
- retweeted_status には id があり、これはリツイート元のツイートidである。
- 目的: リツイート元のツイートidが使用しているデータベース内に存在しているのかを特定する

1. retweeted_status.id をテキストファイルに格納する。同時にすべてのtweet_idも格納する
  - `/work/s245302/Ota-Workspace/data/twitter_stream/sample-archive_ja/{month}/{file}.txt` -> `/work/s245302/Ota-Workspace/data/twitter_stream/ja_retweet_ids/{month}.txt`, `/work/s245302/Ota-Workspace/data/twitter_stream/ja_tweet_ids/{month}.txt`
  - `get_all_retweeted_id.sh`: `INPUT_PATH`, `RETWEET_PATH`, `TWEET_PATH` を `src/twitter_stream/get_retweeted_id.py` に渡す。
  - `src/twitter_stream/get_retweeted_id.py`: `retweeted_status` があるツイートを見つけ出し、そこから `retweeted_status.id` をとってきて、`retweeted_ids` に格納し、出力。ついでに `tweet_id` も出力。

2. retweeted_id.id が tweet_id の中にあるかを確認する
  (1) すべての `retweeted_id` と `tweet_id` をそれぞれ set に入れて引き算で比較。
  - `/work/s245302/Ota-Workspace/data/twitter_stream/ja_retweet_ids/`, `/work/s245302/Ota-Workspace/data/twitter_stream/ja_tweet_ids/` -> `/work/s245302/Ota-Workspace/data/twitter_stream/ja_only_retweets.txt`, `/work/s245302/Ota-Workspace/data/twitter_stream/ja_common_ids.txt`
  - `run.sh` で python ファイルを実行する
  - `src/twitter_stream/compare_tweet_retweet.py`: retweet_ids_path, tweet_tds_path を読み込んで、それぞれ set() を作成する。Set 同士の差集合、積集合を取って出力。


## フォルダ構成
src
  - change2balance_data.py
  - csv2md_table.py
  - label_rate_analyze.py
  lora_multiclassification
  perspective_api_toxicity
  setfit_fewshot
  twitter_stream
    - get_tweet.py: 