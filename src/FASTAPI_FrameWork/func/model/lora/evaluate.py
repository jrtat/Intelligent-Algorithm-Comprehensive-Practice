import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel
from datasets import load_from_disk
from src.RelationGraph.func.utils.calc_top_k import top_k_accuracy


class TextDataset(Dataset): # 用于 DataLoader 批处理
    def __init__(self, texts):
        self.texts = texts

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.texts[idx]


def lora_predict_and_evaluate(model_path, base_model_name, num_labels,
                                dataset_path, top_k_list=None):

    # Step 1： 设备配置和加载分词器&模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    base_model = AutoModelForSequenceClassification.from_pretrained(
        base_model_name, num_labels=num_labels
    )
    model = PeftModel.from_pretrained(base_model, model_path)
    model.eval()
    model.to(device)

    # Step 2：加载测试数据
    dataset = load_from_disk(dataset_path)
    test_data = dataset["test"]
    texts = test_data["text"]
    if "label_id" in test_data.column_names:
        y_test = np.array(test_data["label_id"])
    elif "labels" in test_data.column_names:
        y_test = np.array(test_data["labels"])
    else:
        raise KeyError("测试集中未找到标签列（'label_id' 或 'labels'）")
    print(f"测试集大小：{len(texts)} 条样本")

    def collate_fn(batch):
        enc = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
        return enc

    # Step 3：构建 DataLoader
    dataset_obj = TextDataset(texts)
    loader = DataLoader(
        dataset_obj,
        batch_size=32,
        shuffle=False,
        collate_fn=collate_fn,
    )

    # Step 4：执行分词
    all_probs = []
    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            all_probs.append(probs.cpu().numpy())

    proba = np.vstack(all_probs)

    # Step 5：计算评估值并返回
    pred = np.argmax(proba, axis=1)
    acc = accuracy_score(y_test, pred)
    f1 = f1_score(y_test, pred, average="macro")
    print(f"LoRA 模型测试集结果 | Accuracy: {acc:.4f} | Macro F1: {f1:.4f}")

    if top_k_list is not None:
        topk = top_k_accuracy(proba, y_test, top_k_list)
        for k, v in topk.items():
            print(f"Top-{k} Accuracy: {v:.4f}")
        return proba, topk

    return proba
