import json
import torch
import argparse
from transformers import AutoTokenizer, AutoModel, BitsAndBytesConfig

class CustomPredictor:
	def __init__(self, model_dir):
		self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
		self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
		
		# 量子化設定
		use_bf16 = torch.cuda.is_bf16_supported()
		self.torch_dtype = torch.bfloat16 if use_bf16 else torch.float16
		
		quantization_config = BitsAndBytesConfig(
			load_in_4bit=True,
			bnb_4bit_quant_type="nf4",
			bnb_4bit_use_double_quant=True,
			bnb_4bit_compute_dtype=self.torch_dtype,
		)
		
		# モデルの読み込み（量子化と自動デバイス割り当てを使用）
		self.model = AutoModel.from_pretrained(
			model_dir,
			device_map="auto",  # 複数GPUがある場合に分散配置
			torch_dtype=self.torch_dtype,
			trust_remote_code=True,
			quantization_config=quantization_config
		)
		
		# モデルをeval() モードに
		self.model.eval()
		
		# 分類層の作成（GPUメモリ使用量削減のため小さなバッチサイズを使用）
		self.hidden_size = self.model.config.hidden_size
		self.num_categories = 7
		self.classifiers = [
			torch.nn.Linear(self.hidden_size, 2, dtype=self.torch_dtype).to(self.device)
			for _ in range(self.num_categories)
		]
		
		# カテゴリーの定義
		self.categories = ['obscene', 'discriminatory', 'violent', 'illegal', 'personal', 'corporate', 'others']
	
	def predict(self, texts, batch_size=4):
		# バッチサイズを小さくして予測
		results = []
		
		for i in range(0, len(texts), batch_size):
			batch_texts = texts[i:i+batch_size]
			
			# テキストのエンコード
			inputs = self.tokenizer(batch_texts, return_tensors="pt", padding=True, truncation=True)
			
			# LlamaModelは token_type_ids を受け付けないので削除
			if 'token_type_ids' in inputs:
				del inputs['token_type_ids']
			
			# デバイスに転送
			inputs = {k: v.to(self.device) for k, v in inputs.items()}
			
			with torch.no_grad():
				# メモリ効率のためキャッシュをクリア
				torch.cuda.empty_cache()
				
				# モデルの出力取得
				outputs = self.model(**inputs)
				last_hidden_state = outputs.last_hidden_state
				
				# 各シーケンスの最後のトークンの状態を取得
				seq_lengths = inputs['attention_mask'].sum(dim=1) - 1
				current_batch_size = seq_lengths.size(0)
				batch_indices = torch.arange(current_batch_size, device=self.device)
				sequence_outputs = last_hidden_state[batch_indices, seq_lengths]
				
				# 各カテゴリーの予測
				for batch_idx in range(current_batch_size):
					item_output = sequence_outputs[batch_idx]
					prediction = {}
					
					# 各カテゴリーごとの予測
					for cat_idx, category in enumerate(self.categories):
						# データ型が一致していることを確認
						if item_output.dtype != self.torch_dtype:
							item_output = item_output.to(self.torch_dtype)
						
						logits = self.classifiers[cat_idx](item_output.unsqueeze(0))
						# 単純にポジティブクラスの logit が 0 より大きいかで判定
						pred_value = 1 if logits[0, 1] > logits[0, 0] else 0
						prediction[category] = pred_value
					
					results.append(prediction)
		
		return results


def main(model_dir, input_path, output_path):
	predictor = CustomPredictor(model_dir)
	
	# 入力データの読み込み
	with open(input_path, "r") as f:
		data = [json.loads(line) for line in f]
	
	texts = [item["text"] for item in data]
	
	# IDフィールドの特定
	id_field = "tweet_id" if "tweet_id" in data[0] else "id"
	ids = [item[id_field] for item in data]
	
	# 予測実行
	predictions = predictor.predict(texts)
	
	# 結果の作成と保存
	results = [{"tweet_id": id_val, "prediction": pred} for id_val, pred in zip(ids, predictions)]
	
	with open(output_path, "w") as f:
		json.dump(results, f, indent=4, ensure_ascii=False)
	
	print(f"Saved predictions to {output_path}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--model_dir", type=str, required=True, help="Directory containing the model files")
	parser.add_argument("--input_path", type=str, required=True, help="Path to input data")
	parser.add_argument("--output_path", type=str, required=True, help="Path to save predictions")
	args = parser.parse_args()
	
	main(args.model_dir, args.input_path, args.output_path)
