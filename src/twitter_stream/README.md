# 日本語ツイートの抽出
- get_all_ja_tw_data.sh: 月毎のジョブを発行し get_ja_tw_data.shを呼び出す
- get_ja_tw_data.sh: １時間ごとのツイートを保存したファイルから、“lang”:“ja”が含まれる行のみを抽出する(ざっくりとした日本語抽出)。さらに、src/twitter_stream/filter_ja_tweets.pyを実行する
	- 入力: data/twitter_stream/sample-archive-twitterstream/
	- 出力: data/twitter_stream/sample-archive_str_ja1/
```
grep '"lang":"ja"' $file > "$ja1_file"
```
- src/twitter_stream/filter_ja_tweets.py: jsonデータを読み込んで、langフィールドかuser.langフィールドがjaのデータを抽出(日本語抽出)
	- 入力: data/twitter_stream/sample-archive_str_ja1/
	- 出力: data/twitter_stream/sample-archive_str_ja2/
```
json_data = json.loads(json_str)
lang = json_data.get('lang', '')
if not lang:
	lang = json_data.get('user', {}).get('lang', '')
if lang == 'ja':
	out_list.append(line)
```

# ランダムサンプリング&json整形
- sample_ja2json_all.sh: 月毎のジョブを発行して sample_ja2json_month.sh を実行
- sample_ja2json_month.sh: 指定した月で sample_ja2json.py を実行
- sample_ja2json.py: ランダムサンプリングをして、必要なフィールドだけを抽出した json に整形する。
	- 入力: data/twitter_stream/sampled-ja-0_001/
	- 出力: data/twitter_stream/sampled_ja2json-0_001/

- 土屋先生のデータをコピーする
- data/twitter_stream/sampled-ja-0_001/
- このフォルダはサンプリングまでをやってくれている。そこから、json整形をする必要がある


# 有害ラベル付与
- set_all_toxic_label.sh: 月毎のジョブを発行して set_month_toxic_label.sh を実行
- set_month_toxic_label.sh: 指定した月で src/setfit/setfit_predict.py を実行
- src/setfit/setfit_predict.py: 現在のjsonデータに7つの有害ラベルを付与
	- 入力: data/twitter_stream/sampled-ja-0_001/
	- 出力: data/twitter_stream/sampled-toxic_ja-0_001/
	- 学習元データセット: data/llmjp_toxicity_dataset/train_len4_dataset.jsonl
	- 学習済みモデル: models/few-shot/ruri-v3-310m_len1024_yesno4

# 有害テキスト分類

## 0. 有害投稿の割合
- src/twitter_stream/new_group_analyze/0-1_filter_ja_sampling.py
	- まず、日本語投稿を抽出して、ランダムサンプリングを行う。

- src/twitter_stream/new_group_analyze/0-2_format_json.py
	- 次に、ツイートのjsonデータを成形して必要な情報のみを取り出す

- src/twitter_stream/new_group_analyze/0-3_setfit_predict.py
	- 有害ラベルを付与

- new_group_analyze_0-4_count_toxic.sh
	- 有害投稿数を月毎に計算
	- 有害投稿データ: data/twitter_stream/sampled-toxic_ja-0_001/
	- 表: tables/new_group_analyze/0-4_toxic_count.csv

- src/twitter_stream/new_group_analyze/0-5_make_toxic_count_graph.py
	- 有害投稿数を月毎にグラフにする
	- 表: tables/new_group_analyze/0-4_toxic_count.csv
	- グラフ: imgs/new_group_analyze/0-4_toxic_count.png

## 1. ユーザの利用年数による分類
- src/twitter_stream/new_group_analyze/1-1_grouping_by_usage_years.py
	- 各ユーザの初投稿月を保存
	- 各月のファイルを見て、ユーザ、年月を取得
	- ユーザリストから初投稿つきを取得し、年数を算出
	- 有害投稿データ: data/twitter_stream/sampled-toxic_ja-0_001/
	- ユーザリスト: tables/new_group_analyze/1-1_user_fast_month.json
	- 表: tables/new_group_analyze/1-1_usage_group/

- src/twitter_stream/new_group_analyze/1-2_make_usage_graph.py
	- 表: tables/new_group_analyze/1-1_usage_group/
	- グラフ: imgs/new_group_analyze/1-2_usage_group/

## 2. 投稿の文字数による分類
- src/twitter_stream/new_group_analyze/2-1_count_text_len.py
	- まず、投稿の文字数の分布を出力する
	- 投稿文字数をカウントし、文字数ごとの出現回数を数える。それらを表とグラフにする
	- 有害投稿データ: data/twitter_stream/sampled-toxic_ja-0_001/
	- 表: tables/new_group_analyze/2-1_text_len.csv
	- グラフ: imgs/new_group_analyze/2-1_text_len.png

- 出力から、どのように分類をすればいいかを決定する(前回はグループ1が10~80文字, グループ2が81文字以上)
	- グラフの概形は前回とそれほど変わっていなかった。

- 次に、決定した分類方法に従いラベル付けをする
- src/twitter_stream/new_group_analyze/2-2_grouping_by_textlength.py
	- グループ1(仮:10~80)とグループ2(仮:81~)の投稿数を月毎・有害ラベルごとに算出する
	- noise_len: 10
	- labeling_len: 80
	- 有害投稿データ: data/twitter_stream/sampled-toxic_ja-0_001/
	- 表: tables/new_group_analyze/2-2_textlen_group/

- src/twitter_stream/new_group_analyze/2-3_make_textlength_graph.py
	- グループ1, 2 の割合を月毎・有害ラベルごとに出力
	- 表: tables/new_group_analyze/2-2_textlen_group/
	- グラフ: imgs/new_group_analyze/2-3_textlen_group/


## 3. 投稿に添付されているメディア・URLの有無による分類
- src/twitter_stream/new_group_analyze/3-1_grouping_by_media.py
	- 成形済みのjsonデータのurls, media要素に値が入っているかを確認する
	- 有害投稿データ: data/twitter_stream/sampled-toxic_ja-0_001/
	- 表: tables/new_group_analyze/3-1_media_group/

- src/twitter_stream/new_group_analyze/3-2_make_media_graph.py
	- 分類結果の表をグラフに出力
	- 表: tables/new_group_analyze/3-1_media_group/
	- グラフ: imgs/new_group_analyze/3-2_media_graph/


## 4. 投稿をしている端末による分類
- src/twitter_stream/new_group_analyze/4-1_count_machine.py
	-  端末ランキングとホストランキングを出力する
	- 有害投稿データ: data/twitter_stream/sampled-toxic_ja-0_001/
	- 端末リスト: tables/new_group_analyze/4-1_count_machine/machine_count.txt
	- ホストリスト: tables/new_group_analyze/4-1_count_machine/host_count.txt

- src/twitter_stream/new_group_analyze/4-2_grouping_by_machine.py
	- 成形済みのjsonデータのmachine要素の値を集計する
	- 有害投稿データ: data/twitter_stream/sampled-toxic_ja-0_001/
	- 表: tables/new_group_analyze/4-2_machine_group/

- src/twitter_stream/new_group_analyze/4-3_make_machine_graph.py
	- 分類結果の表をグラフに出力
	- 表: tables/new_group_analyze/4-2_machine_group/
	- グラフ: imgs/new_group_analyze/4-3_machine_graph/


<!-- ## コード
- concat_csv.py: 2つのテーブルを結合して新しいテーブルにして出力
- get_tweet.py: ランダムでツイートを選んで辞書型で出力
	- 入力形式
	```txt
	tweet_id  tweet_json
	tweet_id  tweet_json
	...
	tweet_id  tweet_json
	```
	- 出力形式
	```json
	{
		"tweet_id": "tweet_text",
		"tweet_id": "tweet_text",
		..,
		"tweet_id": "tweet_text"
	}
	```

- sample_hour1000_tweets.py: テキストファイルからランダムでツイートを選んで辞書型で出力
	- 入力形式
	```txt
	tweet_id  tweet_json
	tweet_id  tweet_json
	...
	tweet_id  tweet_json
	```
	- 出力形式
	```json
	{"tweet_id": "1111111111", "text": "ツイート", "user_id": 123456789, "screen_name": "yamada1234", "time": "YYYY-MM-DD-HH", "month": "YYYY-MM"}
	{"tweet_id": "1111111111", "text": "ツイート", "user_id": 123456789, "screen_name": "yamada1234", "time": "YYYY-MM-DD-HH", "month": "YYYY-MM"}
	..
	{"tweet_id": "1111111111", "text": "ツイート", "user_id": 123456789, "screen_name": "yamada1234", "time": "YYYY-MM-DD-HH", "month": "YYYY-MM"}
	```

- calc_random_toxic_user_tweets.py: ランダムで有害ユーザを選択して、そのユーザの各月での投稿数を集計する。保留
- count_toxic_user.py: 月毎の有害ラベルが付与されたツイートから、有害ツイートをしているユーザと有害投稿数を算出して出力。さらに、月毎で有害ユーザ数を算出
	- 入力形式
	```json
	{"tweet_id": "1111111111", "text": "ツイート", "user_id": 123456789, "screen_name": "yamada1234", "time": "YYYY-MM-DD-HH", "month": "YYYY-MM", "personal": 0, "others": 0, "illegal": 0, "corporate": 0, "violent": 0, "discriminatory": 0, "obscene": 0}
	{"tweet_id": "1111111111", "text": "ツイート", "user_id": 123456789, "screen_name": "yamada1234", "time": "YYYY-MM-DD-HH", "month": "YYYY-MM", "personal": 0, "others": 0, "illegal": 0, "corporate": 0, "violent": 0, "discriminatory": 0, "obscene": 0}
	..
	{"tweet_id": "1111111111", "text": "ツイート", "user_id": 123456789, "screen_name": "yamada1234", "time": "YYYY-MM-DD-HH", "month": "YYYY-MM", "personal": 0, "others": 0, "illegal": 0, "corporate": 0, "violent": 0, "discriminatory": 0, "obscene": 0}
	```
	- 出力形式1(特定の月の有害ユーザのtoxicごとの有害投稿数)
	```csv
	toxic_user,obscene,discriminatory,violent
	123456789,0,1,1
	123456789,0,0,1
	..
	123456789,0,1,1
	```
	- 出力形式2(月毎のtoxicごとの有害ユーザ数)
	```csv
	,obscene,discriminatory,violent
	2011-09,1111,222,333
	2011-10,1111,222,333
	..
	2021-08,1111,222,333
	```

- make_toxic_user_list.py: 有害投稿をしているユーザidを一つのテキストファイルに出力
	- 入力形式
	```csv
		toxic_user,obscene,discriminatory,violent
	2408361,0,1,1
	3271411,0,0,1
	..
	4674371,0,1,1
	```
	- 出力形式
	```txt
	123456789
	123456789
	..
	123456789
	```

- compare_tweet_retweet.py: 
- get_retweeted_id.py: 全てのtweet_idと全てのリツイート元tweet_id(以後retweet_id)をテキストファイルに保存
	- 入力形式
	```txt
	tweet_id  tweet_json
	tweet_id  tweet_json
	...
	tweet_id  tweet_json

	```
	- 出力形式(tweet_ids, retweet_ids)
	```txt
	123456789
	123456789
	..
	123456789
	```
- sample_100_tweet.py: sample_hour1000_tweets.pyの前のバージョン。ランダムで100ツイートを選ぶバージョン -->
