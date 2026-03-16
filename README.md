# Ota-Workspace について
- 何をしている？：ツイートデータから有害ツイートを抽出してその割合を分析している。
- 有害ツイートの抽出方法は？：multiclassification で作成した 『setfit による few-shot 学習を用いた有害テキスト判定モデル』を使用
- setfit の学習・評価には有害テキストデータセット『LLM-jp Toxicity Dataset v2』を使用した
- ツイートデータは取得方法は？：技科大の吉田先生のアカウントに格納されているデータをコピーして使用している

# フォルダ・ファイル構成
- .venv: python のライブラリのバージョンを管理するのに使用。ここは触らない。
- data: 取ってきたデータや出力されたデータ。基本的にはツイートデータや有害テキストデータセットを格納
	- llmjp_toxicity_dataset: 有害テキストデータセット。有害テキスト判定モデルの学習・評価に使用
	- perspective_api_toxicity: Perspective API を用いて有害ラベルが付与されたツイート。吉田先生から提供していただいたが、研究では使わなかった。
	- twitter_steram: 分析に使用した、ツイートデータ。技科大のクラスタの中の吉田先生のアカウントに格納されているツイートデータをコピーしている。
- imgs: 分析結果などの画像を格納
- log: `qsub XX.sh` でジョブを実行したときに、生成されるジョブのログファイルを格納
- models: `outputs` フォルダで生成されたモデルのうち、分析に使用するものを手動で格納
	- lora-multiclassification/llm-jp-3-1.8b_len1024_yesno16: llm-jp を用いて LLM+LoRA 学習をした結果
	- few-shot/ruri-v3-310m_len1024_yesno4: ruri を用いて setfit 学習をした結果
- outputs: `qsub XX.sh` でモデルを学習するジョブを実行したときに生成されるモデルを自動で格納
	- llm-jp-3-1.8b: llm-jp を用いて LLM+LoRA 学習をした結果
	- ruri-v3-310m: ruri を用いて setfit 学習をした結果
- run_sh_archive: 過去使用していたジョブファイル(`.sh`)を格納
- src: 実行するソースコード(基本的には `.py`)を格納
	- lora_multiclassification: 『LLM+LoRA による有害テキスト判定モデル』の作成に使用したソースコード
	- perspective_api_toxicity: 吉田先生に提供していただいた、Perspectvie API を用いてツイートに有害ラベルを付与したデータ(格納場所：`data/perspective_api_toxicity`)の中身の確認
	- setfit_fewshot: 『setfit による few-shot 学習を用いた有害テキスト判定モデル』の作成しに使用したソースコード
	- src_archive: 過去使用していたソースコード
	- twitter_stream: **有害投稿の分析**に使用したソースコード
- tables: 分析結果などの表(`.csv`)を格納

# 有害ツイートの割合の分析
## ツイートデータのコピー
- 学内の計算機にあるツイートデータをこのリポジトリにコピーする
- 元データ: `/work/my016/mirror/twitter-stream/{month}/{file}.txt`
- コピー先: `/work/s245302/Ota-Workspace/data/twitter_stream/{month}/{file}.txt`
- `copy_all_twitter_stream.sh`: `DATA_PATH` から月毎のフォルダ名を取得して、各フォルダ名を `copy_month_twitter_stream.sh` に渡してジョブとして実行している。
- `copy_month_twitter_stream.sh`: `copy_all_twitter_stream.sh` から受け取ったある月のフォルダ名の直下にあるファイルを全て `OUTPUT_PATH` にコピーする。ファイルの解凍は `gunzip` コマンドを使用

## 0. 有害投稿の割合の算出
- `src/twitter_stream/new_group_analyze/0-1_filter_ja_sampling.py`
	- まず、日本語投稿を抽出して、0.1%ランダムサンプリングを行う。
	- all_sh: `tweet_sampling_all.sh`

- `src/twitter_stream/new_group_analyze/0-2_format_json.py`
	- 次に、ツイートのjsonデータを成形して必要な情報のみを取り出す
	- all_sh: `sample_ja2json_all.sh`
		- month_sh: `sample_ja2json_month.sh`
	- 成形前: `data/twitter_stream/sampled-ja-0_001/`
	- 成形後: `data/twitter_stream/sampled_ja2json-0_001/`

- `new_group_analyze_0-3_setfit_predict.sh`
	- 旧: `set_all_toxic_label.sh`
		- 月ごと: `set_month_toxic_label.sh`
	- 有害ラベル付与前: `data/twitter_stream/sampled_ja2json-0_001/`
	- 有害ラベル付与後: `data/twitter_stream/sampled-toxic_ja-0_001/`
	- 有害ラベルを付与

- `new_group_analyze_0-4_count_toxic.sh`
	- 有害投稿数を月毎に計算
	- 有害投稿データ: `data/twitter_stream/sampled-toxic_ja-0_001/`
	- 表: `tables/new_group_analyze/0-4_toxic_count.csv`

- `src/twitter_stream/new_group_analyze/0-5_make_toxic_count_graph.py`
	- 有害投稿数を月毎にグラフにする
	- 表: `tables/new_group_analyze/0-4_toxic_count.csv`
	- グラフ: `imgs/new_group_analyze/0-4_toxic_count.png`

- `src/twitter_stream/new_group_analyze/0-6_make_all_tw_count_graph.py`
	- 投稿数を月毎にグラフにする
	- 表: `tables/new_group_analyze/0-4_toxic_count.csv`
	- グラフ: `imgs/new_group_analyze/0-6_all_tw_count.png`

## 1. ユーザの利用年数による分類
- `src/twitter_stream/new_group_analyze/1-1_grouping_by_usage_years.py`
	- 各ユーザの初投稿月を保存
	- 各月のファイルを見て、ユーザ、年月を取得
	- ユーザリストから初投稿つきを取得し、年数を算出
	- 有害投稿データ: `data/twitter_stream/sampled-toxic_ja-0_001/`
	- ユーザリスト: `tables/new_group_analyze/1-1_user_fast_month.json`
	- 表: `tables/new_group_analyze/1-1_usage_group/`

- `src/twitter_stream/new_group_analyze/1-2_make_usage_graph.py`
	- 表: `tables/new_group_analyze/1-1_usage_group/`
	- グラフ: `imgs/new_group_analyze/1-2_usage_group/`

## 2. 投稿の文字数による分類
- `src/twitter_stream/new_group_analyze/2-1_count_text_len.py`
	- まず、投稿の文字数の分布を出力する
	- 投稿文字数をカウントし、文字数ごとの出現回数を数える。それらを表とグラフにする
	- 有害投稿データ: `data/twitter_stream/sampled-toxic_ja-0_001/`
	- 表: `tables/new_group_analyze/2-1_text_len.csv`
	- グラフ: `imgs/new_group_analyze/2-1_text_len.png`

- 出力から、どのように分類をすればいいかを決定する(前回はグループ1が10~80文字, グループ2が81文字以上)
	- グラフの概形は前回とそれほど変わっていなかった。

- 次に、決定した分類方法に従いラベル付けをする
- `src/twitter_stream/new_group_analyze/2-2_grouping_by_textlength.py`
	- グループ1(仮:10~80)とグループ2(仮:81~)の投稿数を月毎・有害ラベルごとに算出する
	- noise_len: 10
	- labeling_len: 80
	- 有害投稿データ: `data/twitter_stream/sampled-toxic_ja-0_001/`
	- 表: `tables/new_group_analyze/2-2_textlen_group/`

- `src/twitter_stream/new_group_analyze/2-3_make_textlength_graph.py`
	- グループ1, 2 の割合を月毎・有害ラベルごとに出力
	- 表: `tables/new_group_analyze/2-2_textlen_group/`
	- グラフ: `imgs/new_group_analyze/2-3_textlen_group/`


## 3. 投稿に添付されているメディア・URLの有無による分類
- `src/twitter_stream/new_group_analyze/3-1_grouping_by_media.py`
	- 成形済みのjsonデータのurls, media要素に値が入っているかを確認する
	- 有害投稿データ: `data/twitter_stream/sampled-toxic_ja-0_001/`
	- 表: `tables/new_group_analyze/3-1_media_group/`

- `src/twitter_stream/new_group_analyze/3-2_make_media_graph.py`
	- 分類結果の表をグラフに出力
	- 表: `tables/new_group_analyze/3-1_media_group/`
	- グラフ: `imgs/new_group_analyze/3-2_media_graph/`


## 4. 投稿をしている端末による分類
- `src/twitter_stream/new_group_analyze/4-1_count_machine.py`
	-  端末ランキングとホストランキングを出力する
	- 有害投稿データ: `data/twitter_stream/sampled-toxic_ja-0_001/`
	- 端末リスト: `tables/new_group_analyze/4-1_count_machine/machine_count.txt`
	- ホストリスト: `tables/new_group_analyze/4-1_count_machine/host_count.txt`

- `src/twitter_stream/new_group_analyze/4-2_grouping_by_machine.py`
	- 成形済みのjsonデータのmachine要素の値を集計する
	- 有害投稿データ: `data/twitter_stream/sampled-toxic_ja-0_001/`
	- 表: `tables/new_group_analyze/4-2_machine_group/`

- `src/twitter_stream/new_group_analyze/4-3_make_machine_graph.py`
	- 分類結果の表をグラフに出力
	- 表: `tables/new_group_analyze/4-2_machine_group/`
	- グラフ: `imgs/new_group_analyze/4-3_machine_graph/`

# 番外編1: llmjp-toxicity-dataset v2 をできるだけ均衡データに近づける
- 使用するデータセットは各ラベルについて全体に対する有害なデータの割合がとても少ない(不均衡データ)。
- 目的: そこで、有害でないデータをランダムで選択して削ったデータセットを用意する
- `src/change2balance_data.py`
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

# 番外編2: リツイートしたツイートの元ツイートの格納先の特定
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
