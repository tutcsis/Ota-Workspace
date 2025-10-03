import json
import pandas as pd

# toxicity_dataset_ver2.jsonl の指定したカラムの label の割合を調べる
# 指定するカラム: obscene, discriminatory, violent, illegal, personal, corporate, others
# 確認するデータの行の始めと終わりを指定する。
def jsonl_check_label_ratio(columns, jsonl_path=None, start=0, end=None, output_path=None, data=None):
  if data is None:
    # 1.  データの読み込み
    with open(jsonl_path, 'r', encoding='utf-8') as f:
      data = [json.loads(line) for line in f]

    # 2. 指定した範囲のデータのみを使用
    data = data[start:end]
    if not data:
      print("指定された範囲にデータがありません。")
      return

  # 3. 指定したカラムが存在するか確認
  for column in columns:
    if column not in data[0]:
      print(f"Column '{column}' does not exist in the JSONL file.")
      return
  print('columns: ', columns)

  # 4. 各カラムのラベルの割合を計算
  label_ratios = {}
  # print(f"\nLabel ratio and counts for each column (rows {start} to {end-1 if end is not None else len(data)-1}):")
  for column in columns:
    total_count = len(data)
    yes_count = sum(1 for item in data if item[column] == 'yes')
    no_count = sum(1 for item in data if item[column] == 'no')
    label_ratios[column] = {
        'yes_rate': yes_count / total_count,
        'no_rate': no_count / total_count,
        'yes_count': yes_count,
        'no_count': no_count,
    }
    print(f"'{column}': yes..{label_ratios[column]['yes_rate']:.2%}({yes_count}), no..{label_ratios[column]['no_rate']:.2%}({no_count})")

  # 5. csv ファイルに保存
  # columns: obscene, discriminatory, violent, illegal, personal, corporate, others
  # rows: yes_rate, no_rate, yes_count, no_count
  df = pd.DataFrame(label_ratios)
  df = df.transpose()  # カラム名を行に、測定値を列にするために転置
  df['yes_rate'] = df['yes_rate'].map(lambda x: float(f'{x:.4g}'))
  df['no_rate'] = df['no_rate'].map(lambda x: float(f'{x:.4g}'))
  df['yes_count'] = df['yes_count'].astype(int)
  df['no_count'] = df['no_count'].astype(int)
  
  # CSVファイルに保存（output_pathが指定されている場合）
  if output_path:
    df.to_csv(output_path)
    print(f"結果を {output_path} に保存しました。")
  
  return label_ratios

# toxicity_dataset_ver2.jsonl の一つでも yes のラベルのついているデータとそれ以外の数と割合を調べる
# 指定するカラム: obscene, discriminatory, violent, illegal, personal, corporate, others
# 確認するデータの行の始めと終わりを指定する。
def jsonl_all_yesno_rate(columns, jsonl_path, start=0, end=None):
  # 1. data loading..
  count = 0
  yes_count_dict = {str(i): 0 for i in range(len(columns) + 1)}
  with open(jsonl_path, 'r', encoding='utf-8') as f:
    for line in f:
      if count >= start:
        data = json.loads(line)
        yes_count = sum(data[column] == 'yes' for column in columns)
        yes_count_dict[str(yes_count)] += 1
      if count >= end:
        break
      count += 1
    print(yes_count_dict)


def jsonl_delete_allno_data(base, columns, jsonl_path=None, start=0, end=None, filter_columns=None, data_list=[], delete_len=0):
  # 1. data loading..
  count = 0
  output_fields = base + columns
  allno_count = 0
  print(output_fields)
  # if jsonl_path is None:
  #   print('delete_len: ', delete_len)
  #   delete_count = 0
  #   out_data_list = []
  #   for id, data in enumerate(data_list):
  #     exist_yes = all(data[column] == 'no' for column in filter_columns)
  #     if exist_yes and delete_count < delete_len:
  #       delete_count += 1
  #     else:
  #       out_data_list.append(data)
  #   return out_data_list

  with open(jsonl_path, 'r', encoding='utf-8') as f:
    for line in f:
      if count >= start:
        data = json.loads(line)
        if filter_columns != None:
          exist_yes = any(data[column] == 'yes' for column in filter_columns)
        else:
          exist_yes = any(data[column] == 'yes' for column in columns)
        if exist_yes:
          data_list.append({key: data[key] for key in output_fields if key in data})
        else:
          allno_count += 1
      if count >= end:
        break
      count += 1
  print(len(data_list), allno_count)
  return data_list

def jsonl_delete_allyes_data(base, columns, jsonl_path=None, start=0, end=None):
  data_list = []
  count = 0
  with open(jsonl_path, 'r', encoding='utf-8') as f:
    for line in f:
      if count < start:
        count += 1
        continue
      if count >= end:
        break
      data = json.loads(line)
      exist_yes = any(data[columns] == 'yes' for columns in columns)
      if not exist_yes:
        data_list.append(data)
      count += 1
  return data_list

def save_to_jsonl(data_list, output_path):
  with open(output_path, 'w', encoding='utf-8') as f:
    for data in data_list:
      json.dump(data, f, ensure_ascii=False)
      f.write('\n')

# columns = ["obscene", "discriminatory", "violent", "illegal", "personal", "corporate", "others"]
# `other`, `illegal`, `personal` のデータの yes の個数が圧倒的に少ないため(どれも 100 未満)、これらは取り除く
base = ["id", "text", "label"]
columns = ["obscene", "discriminatory", "violent", "illegal", "personal", "corporate", "others"]
# filter_columns = ["discriminatory", "corporate"]
jsonl_path = '/work/s245302/multiclassification/data/toxicity_dataset_ver2.jsonl'
output_path = '/work/s245302/multiclassification/analysis_results/toxicity_ver2_label_ratio_downsampling'
# out_data_path = '/work/s245302/multiclassification/data/toxicity_ver2_downsampling.jsonl'
# out_data_path = '/work/s245302/multiclassification/data/toxicity_ver2_allyesdata.jsonl'
out_data_path = '/work/s245302/multiclassification/data/toxicity_ver2_allnodata.jsonl'

# 一つでも `yes` のラベルのついているデータのみ抽出
# print('a: ver1 のデータのみ (1874 件)')
# ver1_data_list = jsonl_delete_allno_data(base, columns, jsonl_path, start=0, end=1847)
# jsonl_check_label_ratio(columns, jsonl_path,  start=0, end=1847, output_path=output_path + '_ver1.csv', data=ver1_data_list)
# jsonl_all_yesno_rate(columns, jsonl_path,  start=0, end=1847, output_path=output_path + '_ver1.csv')

# print('--------------------------')
# print('b: ver2 で新たに追加されたデータ (2000 件)')
# ver2_data_list = jsonl_delete_allno_data(base, columns, jsonl_path, start=1847, end=3847)
# jsonl_check_label_ratio(columns, jsonl_path, start=1847, end=3847, output_path=output_path + '_ver2.csv', data=ver2_data_list)
# jsonl_all_yesno_rate(columns, jsonl_path, start=1847, end=3847, output_path=output_path + '_ver2.csv')
print('--------------------------')
print('c: ver2 のすべてのデータ (3874 件)')
# all_data_list = jsonl_delete_allno_data(base, columns, jsonl_path, start=0, end=3847)
# obscene_yes_count = sum(data['obscene'] == 'yes' for data in all_data_list)
# print(obscene_yes_count, 2*obscene_yes_count-len(all_data_list))
# out_data_list = jsonl_delete_allno_data(base, columns, jsonl_path, start=0, end=3847, filter_columns=None, data_list=all_data_list, delete_len=2*obscene_yes_count-len(all_data_list))
all_no_data_list = jsonl_delete_allyes_data(base, columns, jsonl_path, start=0, end=3847)
save_to_jsonl(all_no_data_list, output_path=out_data_path)
# save_to_jsonl(all_data_list, out_data_path)
# jsonl_check_label_ratio(columns, jsonl_path, output_path=output_path + '_all.csv', data=out_data_list)
