import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel
from datasets import load_from_disk
from RelationGraph.func.utils.calc_top_k import top_k_accuracy


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


def lora_predict_and_evaluate(
    model=None,
    tokenizer=None,
    device=None,
    texts=None,
    y_test=None,
    verbose=True,
    batch_size=32,
    max_length=512,
    top_k_list=None,
    # 从本地加载模型的参数
    model_path=None,
    base_model_name=None,
    num_labels=None,
    # 从本地加载数据的参数
    dataset_path=None
):
    """
    使用 LoRA 微调后的 Transformers 模型对测试集文本进行概率预测。
    支持多种调用方式：

    方式1：直接传入已加载的 model、tokenizer、device 以及 texts 和 y_test。
    方式2：提供 model_path、base_model_name、num_labels 从本地加载模型。
    方式3：提供 dataset_path 从 HuggingFace Dataset 自动加载测试集文本和标签（此时 texts 和 y_test 参数将被忽略）。

    参数:
        model (PreTrainedModel, optional): 已加载的 PEFT 模型（已调用 model.eval()）
        tokenizer (PreTrainedTokenizer, optional): 对应的分词器
        device (torch.device, optional): 计算设备
        texts (list of str, optional): 测试文本列表
        y_test (np.ndarray, optional): 测试标签
        verbose (bool): 是否打印评估结果
        batch_size (int): 推理时的批次大小
        max_length (int): 分词时的最大长度
        top_k_list (tuple or list, optional): 如 (1, 3, 5)，计算对应 Top-k 准确率
        model_path (str, optional): 保存 LoRA 适配器权重的本地路径
        base_model_name (str, optional): 基础模型名称
        num_labels (int, optional): 分类类别数
        dataset_path (str, optional): HuggingFace Dataset 保存路径（如 "./func/model/lora/job_classify_dataset_aug"）

    返回:
        若 y_test 不为 None 且 top_k_list 不为 None，返回 (proba, topk_dict)
        否则返回 proba (np.ndarray)
    """
    # ----- 从本地路径加载模型与分词器 -----
    if model_path is not None and base_model_name is not None and num_labels is not None:
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        base_model = AutoModelForSequenceClassification.from_pretrained(
            base_model_name,
            num_labels=num_labels
        )
        model = PeftModel.from_pretrained(base_model, model_path)
        model.eval()
        model.to(device)
        if verbose:
            print(f"已从 {model_path} 加载 LoRA 模型，基础模型: {base_model_name}")
    else:
        if model is None or tokenizer is None or device is None:
            raise ValueError(
                "必须提供 model、tokenizer、device，或提供 model_path、base_model_name、num_labels 以从本地加载模型。"
            )

    # ----- 从数据集路径加载测试文本与标签 -----
    if dataset_path is not None:
        if verbose:
            print(f"从 {dataset_path} 加载测试数据集...")
        dataset = load_from_disk(dataset_path)
        test_data = dataset["test"]
        texts = test_data["text"]
        # 兼容列名：可能是 'label_id' 或 'labels'
        if "label_id" in test_data.column_names:
            y_test = np.array(test_data["label_id"])
        elif "labels" in test_data.column_names:
            y_test = np.array(test_data["labels"])
        else:
            raise KeyError("测试集中未找到标签列（'label_id' 或 'labels'）")
        if verbose:
            print(f"测试集大小：{len(texts)} 条样本")

    if texts is None:
        raise ValueError("未提供测试文本，请通过 texts 参数传入或指定 dataset_path。")

    # ----- 推理与评估 -----
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