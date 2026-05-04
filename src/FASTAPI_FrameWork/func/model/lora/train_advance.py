from src.RelationGraph.func.utils.config import model_path, dataset_path, model_name

import torch
import torch.nn.functional as F
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding,
    EarlyStoppingCallback
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_from_disk
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

class AdvancedTrainer(Trainer): # 继承自Trainer
    def __init__(self, *args, gamma=2.0, alpha=None, rdrop_alpha=0.5, **kwargs): # 初始化函数
        super().__init__(*args, **kwargs)
        self.gamma = gamma
        self.alpha = alpha
        self.rdrop_alpha = rdrop_alpha

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None): # Trainer 在每一步训练时自动调用的方法，用于计算损失值
        labels = inputs.pop("labels") # 提取标签并移除

        outputs1 = model(**inputs)
        outputs2 = model(**inputs)
        logits1, logits2 = outputs1.logits, outputs2.logits
        # 正常训练时，模型对一批数据只前向一次。这里故意跑了两次，两次前向过程中 Dropout 层的随机丢弃模式不同，所以 logits1 和 logits2 会略有差异。
        # 这正是 R-Drop 的核心思想：希望模型对同一个样本（两次随机 Dropout 后）输出尽量一致的分布，从而增强模型的鲁棒性和泛化能力。

        ce_loss1 = F.cross_entropy(logits1, labels, reduction='none')
        ce_loss2 = F.cross_entropy(logits2, labels, reduction='none')
        # 这里先算出每个样本的交叉熵损失，reduction='none' 表示保留每个样本独立的损失值，形状为 [batch_size]

        pt1 = torch.exp(-ce_loss1)
        pt2 = torch.exp(-ce_loss2)
        # 交叉熵的定义是 -log(p)，其中 p 是模型对真实类别的预测概率。
        # 取指数 exp(-ce_loss1) 正好还原出 p，这个 pt 就代表 模型对正确类别的预测置信度

        focal_loss1 = ((1 - pt1) ** self.gamma) * ce_loss1
        focal_loss2 = ((1 - pt2) ** self.gamma) * ce_loss2
        # Focal Loss 的公式：FL(p) = (1 - p)^γ * CE(p)
        #   如果模型对一个样本预测得很准（p 接近 1），(1-p)^γ 会非常小，这个样本的损失被大幅压低
        #   如果预测得很差（p 接近 0），权重接近 1，损失几乎不变

        if self.alpha is not None: # 当前项目还用不上这个，暂且保留
            focal_loss1 = self.alpha[labels] * focal_loss1
            focal_loss2 = self.alpha[labels] * focal_loss2
        ce_loss = (focal_loss1.mean() + focal_loss2.mean()) * 0.5
        # 两次前向的 Focal Loss 取平均，作为分类损失的主体部分
        # alpha 是类别权重，可以手动传入一个列表（例如 [0.5, 1.0, 2.0]），对不同类别的重要性做额外加权

        kl1 = F.kl_div(F.log_softmax(logits1, dim=-1), F.softmax(logits2, dim=-1), reduction='batchmean')
        kl2 = F.kl_div(F.log_softmax(logits2, dim=-1), F.softmax(logits1, dim=-1), reduction='batchmean')
        kl_loss = (kl1 + kl2) * 0.5
        # 这个 KL 值衡量了两次前向输出的差异。如果 Dropout 导致模型输出剧烈波动，KL 散度就会很大，从而被惩罚。
        # 通过最小化这个正则项，模型学会了对不同 Dropout 噪声保持预测一致性。

        loss = ce_loss + self.rdrop_alpha * kl_loss
        # ce_loss：两次前向 Focal Loss 的平均值，负责让模型分对类别
        # kl_loss：R-Drop 的正则项，负责让模型输出稳定
        # rdrop_alpha：正则项系数，控制一致性约束的强弱

        return (loss, outputs1) if return_outputs else loss
        # 如果调用者需要拿到模型输出，就返回元组 (loss, outputs1)，否则只返回标量损失

def train_and_evaluate_lora():

    # Step 1：读入数据集
    dataset = load_from_disk(dataset_path)
    num_labels = len(set(dataset["train"]["label_id"]))

    print(f"训练集分类数：{num_labels}")

    # Step 2：选择tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=512)

    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    # 使用 chinese-macbert-large 的 tokenizer 对文本列 text 进行分词，截断到最大长度 512
    tokenized_datasets = tokenized_datasets.rename_column("label_id", "labels")
    # 将标签列名由 label_id 改为 Trainer 默认期望的 labels

    # Step 3：配置各种参数 & 各种实例化
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS, # 指定当前任务类型为 序列分类
        r=32, # LoRA 的 秩（Rank），即低秩分解矩阵的维度，区间为0-64，分类任务较为复杂，r应当更高
        lora_alpha=64, # LoRA 的 缩放因子，alpha 越大，LoRA 权重的影响越大，通常将 alpha 设为 r 的 1~2 倍
        lora_dropout=0.2, # 在 LoRA 的适配器层中应用 Dropout 的概率
        target_modules=["query", "key", "value", "dense"], # 指定在模型的 哪些模块 上插入 LoRA 适配器
    ) # LoRA 配置

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        dtype=torch.bfloat16, # 将模型转换为 BFloat16 精度以节省显存并加速训练
    ) # 加载预训练 chinese-macbert-large，添加分类头（输出维度 = num_labels）
    model = get_peft_model(model, lora_config) # 用 PEFT 包装模型，注入 LoRA 适配器，此时只有 LoRA 参数和分类头参数是可训练的

    training_args = TrainingArguments(
        output_dir="./func/model/lora/results", # 模型检查点、日志和最终模型的保存目录。训练过程中每个 epoch 保存的模型会存放在此
        learning_rate=2e-4,  # AdamW 优化器的初始学习率。所有可训练参数（LoRA + 分类头）使用此学习率
        per_device_train_batch_size=4, # 每张 GPU 上每次前向传播的样本数。由于使用了 gradient_accumulation_steps，实际逻辑批次大小会相乘
        per_device_eval_batch_size=32, # 评估时每张 GPU 的批次大小。评估不需梯度，可设较大值以加速
        gradient_accumulation_steps=2, # 梯度累积步数：执行 2 次
        lr_scheduler_type="cosine", # 学习率调度策略。cosine 表示余弦退火：学习率从初始值开始，按余弦曲线衰减至接近 0
        warmup_ratio=0.1, # 预热步数占总训练步数的比例。前 10% 的训练步数内，学习率从 0 线性增长到 learning_rate，稳定训练初期
        num_train_epochs= 10, # 完整遍历训练数据集的次数。结合早停机制（EarlyStoppingCallback），实际可能在更少 epoch 停止
        weight_decay=0.01, # 权重衰减系数（L2 正则化），作用于所有非偏置、非 LayerNorm 的参数，防止过拟合
        eval_strategy="epoch", # 评估策略：每个 epoch 结束时在验证集上运行评估
        save_strategy="epoch", # 模型保存策略：每个 epoch 结束时保存一次检查点
        load_best_model_at_end=True, # 训练结束后自动加载验证集上表现最佳的模型（根据 metric_for_best_model）
        metric_for_best_model="accuracy", # 指定以哪个评估指标作为选择最佳模型的依据。这里选择准确率
        bf16=True, # 启用 BFloat16 混合精度训练。要求 GPU 支持 Ampere 架构及以上。可显著降低显存占用并加速训练，同时保持数值稳定性
        logging_steps=50, # 每隔多少个训练步数记录一次损失、学习率等指标。
        report_to="none", # 禁用向第三方平台（如 WandB、TensorBoard）自动上报日志。训练日志仅输出到控制台
        label_smoothing_factor=0.05, # 标签平滑系数。将硬标签（如 [0,1,0]）替换为软标签（如 [0.025,0.95,0.025]），强制模型降低对预测的置信度，提升泛化能力、缓解过拟合
        optim="adamw_torch" # 指定使用的优化器。adamw_torch 是 PyTorch 原生实现的 AdamW（带解耦权重衰减），稳定性好。
    )

    def compute_metrics(eval_pred): # 该函数用于计算准确率和宏平均 F1
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        acc = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average="macro")
        return {"accuracy": acc, "f1_macro": f1}

    trainer = AdvancedTrainer(
        model=model, # 要训练的模型（已注入 LoRA 适配器）
        args=training_args, # 之前定义的 TrainingArguments 对象
        train_dataset=tokenized_datasets["train"], # 数据集
        eval_dataset=tokenized_datasets["validation"], # 验证集
        processing_class=tokenizer, # Trainer 在保存模型时会自动保存 tokenizer，方便后续推理时加载
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer), # 数据整理器，负责将同一批次的样本动态填充到相同长度，形成模型可接受的张量输入
        compute_metrics=compute_metrics, # 之前定义的评估函数
        callbacks=[EarlyStoppingCallback(early_stopping_patience=5)], # 回调函数列表。这里加入早停机制：若验证集指连续 5 个 epoch 未提升，则提前终止训练
        gamma=2.0, # Focal Loss 中的聚焦参数。值越大，对易分类样本的权重抑制越强，模型越聚焦于难分类样本
        rdrop_alpha=0.3, # R-Drop 正则化项的权重系数。控制两次前向输出分布一致性的 KL 散度在总损失中的占比。0.3 表示 KL 损失占总损失的 30% 权重。
    ) # 实例化自定义训练器 AdvancedTrainer

    trainer.train() # 执行训练

    # Step 4：在测试集上执行，并保存模型到本地
    test_results = trainer.predict(tokenized_datasets["test"])
    print("Test F1:", test_results.metrics["test_f1_macro"])
    print("Test Accuracy:", test_results.metrics["test_accuracy"])

    model.save_pretrained(model_path)