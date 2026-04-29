from RelationGraph.func.utils.config import model_path, dataset_path, model_name

import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_from_disk
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

def train_and_evaluate_lora():

    # Step 1：加载数据
    dataset = load_from_disk(dataset_path)
    num_labels = len(set(dataset["train"]["label_id"]))

    print(num_labels)

    # Step 2：加载模型和分词器

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=512)

    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    tokenized_datasets = tokenized_datasets.rename_column("label_id", "labels")

    # Step 3：配置 LoRA
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS, # 任务类型，SEQ_CLS 表示序列分类，决定 LoRA 层的插入位置和输出结构
        inference_mode=False, # 设为 False 表示训练模式，启用 LoRA 参数更新
        r=16, # LoRA 分解矩阵的秩。越大模型容量越高，但参数更多，易过拟合
        lora_alpha=32, # 缩放因子，实际学习率会被缩放为 alpha/r。常设为 2*r
        lora_dropout=0.15, # LoRA 层的 dropout 概率，用于正则化
        target_modules=["query", "key", "value", "dense"], # 指定在哪些模块上添加 LoRA 适配器，如 ["query", "value"] 对注意力 Q/V 矩阵生效
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        dtype=torch.bfloat16,   # 关键改动
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Step 4：配置 TrainingArguments
    training_args = TrainingArguments(
        output_dir= model_path + "/results", # 模型和日志保存路径
        learning_rate=3e-4,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=128,
        lr_scheduler_type="cosine", # 余弦退火，最终衰减至 0
        warmup_ratio=0.1,  # 前 10% 步数线性 warmup
        num_train_epochs=10, # 训练总轮数
        weight_decay=0.01, # AdamW 中的权重衰减系数，正则化项
        eval_strategy="epoch", # 评估时机，"epoch" 每轮结束验证一次
        save_strategy="epoch", # 保存检查点的时机，与 eval_strategy 对齐便于加载最佳模型
        load_best_model_at_end=True, # 训练结束后自动加载验证集上性能最好的模型
        metric_for_best_model="f1_macro", # 指定作为“最佳”评判的指标名称, F1 score
        bf16=True, # 启用 Brain Floating Point 16 位训练，RTX 4060 原生支持，减少显存且数值稳定
        logging_steps=50, # 每多少步打印一次日志
        report_to="none", # 关闭第三方报告（如 wandb）
        label_smoothing_factor=0.08, # 标签平滑，将硬标签转为软标签，防止模型过度自信，提升泛化
        optim="adamw_torch", # 指定优化器类型，adamw_torch 为 PyTorch 原生 AdamW
    )

    # Step 5：配置Trainer
    def compute_metrics(eval_pred): # 验证集计算两个指标的函数
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        acc = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average="macro")
        return {"accuracy": acc, "f1_macro": f1}

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"], # 训练集
        eval_dataset=tokenized_datasets["validation"], # 验证集
        processing_class=tokenizer, # 分词器
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics, # 上面定义的评估函数
    )

    # Step 6：训练并保存模型
    trainer.train() # 训练模型

    test_results = trainer.predict(tokenized_datasets["test"]) # 在测试集上运行模型
    print("Test F1:", test_results.metrics["test_f1_macro"])
    print("Test Accuracy:", test_results.metrics["test_accuracy"])

    model.save_pretrained(model_path) # 保存模型到本地