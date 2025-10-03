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
  - yes_test_dataset: yes_train_dataset 以外の yes_dataset のデータ
3. no_dataset の分割
  - no_train_dataset: yes_train_dataset の個数だけランダムサンプリングで収集
  - no_test_dataset: no_train_dataset 以外の no_dataset のデータ
4. 学習データとテストデータの生成
  - train_dataset: yes_train_dataset + no_train_dataset
  - test_dataset: yes_test_dataset + no_test_dataset
