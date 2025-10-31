
## コード
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
- sample_100_tweet.py: sample_hour1000_tweets.pyの前のバージョン。ランダムで100ツイートを選ぶバージョン
