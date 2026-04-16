import os
import gc # Garbage Collector
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    RobertaTokenizer,
    RobertaForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from sklearn.model_selection import StratifiedKFold
from tqdm import tqdm
from RelationGraph.func.utils import config

class TextDataset(Dataset):
    """用于 BERT 微调的 PyTorch Dataset"""

    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def compute_metrics(eval_pred):
    """计算验证集准确率（用于 Early Stopping）"""
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = np.mean(predictions == labels)
    return {'accuracy': accuracy}

def train_bert_fold(train_texts, train_labels, val_texts, val_labels, num_classes, fold_idx, device):
    """
    在单个 fold 上微调 RoBERTa 模型。
    返回微调后的模型和 tokenizer 路径。
    """
    # 加载 tokenizer 和模型
    tokenizer = RobertaTokenizer.from_pretrained(config.MODEL_NAME)
    model = RobertaForSequenceClassification.from_pretrained(
        config.MODEL_NAME,
        num_labels=num_classes,
        ignore_mismatched_sizes=True  # 因为分类头尺寸不同
    )
    model.to(device)

    # 如果启用梯度检查点
    if config.USE_GRADIENT_CHECKPOINT:
        model.gradient_checkpointing_enable()

    # 创建数据集
    train_dataset = TextDataset(train_texts, train_labels, tokenizer, config.MAX_SEQ_LENGTH)
    val_dataset = TextDataset(val_texts, val_labels, tokenizer, config.MAX_SEQ_LENGTH)

    # 训练参数
    output_dir = os.path.join(config.OUTPUT_DIR, f"fold_{fold_idx}")
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=config.NUM_EPOCHS,
        per_device_train_batch_size=config.BATCH_SIZE,
        per_device_eval_batch_size=config.BATCH_SIZE * 2,  # 评估时可以用稍大 batch
        gradient_accumulation_steps=config.GRADIENT_ACCUMULATION_STEPS,
        learning_rate=config.LEARNING_RATE,
        warmup_ratio=0.1,
        weight_decay=0.01,
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        fp16=config.USE_FP16,
        dataloader_drop_last=False,
        report_to="none",  # 不上报 wandb 等
        label_smoothing_factor=config.LABEL_SMOOTHING,  # 关键参数！
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    # 训练
    trainer.train()

    # 保存最终模型
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    # 清理显存
    del model, trainer
    torch.cuda.empty_cache()
    gc.collect()

    return output_dir

def predict_proba_with_model(model_path, texts, device, batch_size=16):
    """
    使用已保存的模型对文本列表进行预测，返回概率矩阵 (n_samples, n_classes)。
    应用温度系数软化概率。
    """
    tokenizer = RobertaTokenizer.from_pretrained(model_path)
    model = RobertaForSequenceClassification.from_pretrained(model_path)
    model.to(device)
    model.eval()

    # 创建临时数据集（无标签）
    class InferenceDataset(Dataset):
        def __init__(self, texts, tokenizer, max_length):
            self.texts = texts
            self.tokenizer = tokenizer
            self.max_length = max_length

        def __len__(self):
            return len(self.texts)

        def __getitem__(self, idx):
            text = str(self.texts[idx])
            encoding = self.tokenizer(
                text,
                truncation=True,
                padding='max_length',
                max_length=self.max_length,
                return_tensors='pt'
            )
            return {
                'input_ids': encoding['input_ids'].squeeze(0),
                'attention_mask': encoding['attention_mask'].squeeze(0)
            }

    dataset = InferenceDataset(texts, tokenizer, config.MAX_SEQ_LENGTH)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    all_probs = []
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="预测概率"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits

            # 应用温度系数软化
            logits = logits / config.TEMPERATURE
            probs = torch.softmax(logits, dim=-1).cpu().numpy()
            all_probs.append(probs)

    # 清理
    del model
    torch.cuda.empty_cache()

    return np.vstack(all_probs)


def bert_calc_proba(device, texts, y, le):
    """
    BERT 微调 + 交叉验证预测概率的主函数。

    参数:
        device: torch 设备
        df: 包含文本列的原始 DataFrame
        y: LabelEncoder 转换后的整数标签 (0 ~ n_classes-1)
        le: LabelEncoder 对象，可以把标签换成文本

    返回:
        proba: 与输入样本顺序相同的概率矩阵 (n_samples, n_classes)
    """
    # 1. 准备文本
    print("正在准备文本数据...")
    num_classes = len(le.classes_)

    # 2. 初始化 K-Fold
    skf = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=42)

    # 3. 存储所有样本的预测概率（顺序与原始 df 一致）
    all_proba = np.zeros((len(texts), num_classes))

    # 4. 逐折训练与预测
    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(texts, y)):
        print(f"\n{'=' * 50}")
        print(f"开始第 {fold_idx + 1}/{config.CV_FOLDS} 折训练")
        print(f"{'=' * 50}")

        train_texts = [texts[i] for i in train_idx]
        train_labels = y[train_idx]
        val_texts = [texts[i] for i in val_idx]
        val_labels = y[val_idx]

        # 训练模型
        model_path = train_bert_fold(
            train_texts, train_labels,
            val_texts, val_labels,
            num_classes, fold_idx, device
        )

        # 对验证集（当前 fold 的测试部分）进行预测
        print(f"正在对第 {fold_idx + 1} 折的验证集进行预测...")
        val_proba = predict_proba_with_model(model_path, val_texts, device)

        # 将预测概率填入正确的位置
        all_proba[val_idx] = val_proba

    print("\n所有折训练完成，已生成完整概率矩阵。")
    return all_proba