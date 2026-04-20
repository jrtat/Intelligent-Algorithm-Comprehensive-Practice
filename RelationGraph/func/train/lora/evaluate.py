from RelationGraph.func.utils.calc_top_k import top_k_accuracy

import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, f1_score

class TextDataset(Dataset):
    """简单的文本数据集，用于 DataLoader 批处理"""
    def __init__(self, texts):
        self.texts = texts

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.texts[idx]


def collate_fn(batch, tokenizer, max_length):
    """批处理函数：将文本列表分词并填充为相同长度"""
    encodings = tokenizer(
        batch,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors="pt"
    )
    return encodings


def lora_predict_and_evaluate(model, tokenizer, device, texts, y_test=None,
                              verbose=True, batch_size=32, max_length=512,
                              top_k_list=None):
    """
    使用 LoRA 微调后的 Transformers 模型对测试集文本进行概率预测，
    若提供 y_test 则评估并打印结果。若同时提供 top_k_list，则额外计算 Top-k 准确率。

    参数:
        model (PreTrainedModel): 已加载的 PEFT 模型（已调用 model.eval()）
        tokenizer (PreTrainedTokenizer): 对应的分词器
        device (torch.device): 计算设备
        texts (list of str): 测试文本列表
        y_test (np.ndarray, optional): 测试标签，若提供则计算并打印准确率与 Macro F1
        verbose (bool): 是否打印评估结果（当 y_test 不为 None 时生效）
        batch_size (int): 推理时的批次大小
        max_length (int): 分词时的最大长度
        top_k_list (tuple or list, optional): 如 (1, 3, 5)，计算对应 Top-k 准确率

    返回:
        若 y_test 不为 None 且 top_k_list 不为 None，返回 (proba, topk_dict)
        否则返回 proba (np.ndarray)
    """
    model.eval()
    model.to(device)

    dataset = TextDataset(texts)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=lambda batch: collate_fn(batch, tokenizer, max_length)
    )

    all_probs = []
    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            all_probs.append(probs.cpu().numpy())

    proba = np.vstack(all_probs)

    if y_test is not None:
        pred = np.argmax(proba, axis=1)
        acc = accuracy_score(y_test, pred)
        f1 = f1_score(y_test, pred, average='macro')
        if verbose:
            print(f"LoRA 模型测试集结果 | Accuracy: {acc:.4f} | Macro F1: {f1:.4f}")
        if top_k_list is not None:
            topk = top_k_accuracy(proba, y_test, top_k_list)
            if verbose:
                for k, v in topk.items():
                    print(f"Top-{k} Accuracy: {v:.4f}")
            return proba, topk
    return proba