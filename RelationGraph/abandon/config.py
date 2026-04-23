# 模型与路径配置
MODEL_NAME = "roberta-large-mnli"  # 可替换为 "FacebookAI/roberta-large-mnli"
OUTPUT_DIR = "./bert_finetuned_occupation"  # 微调后模型的保存路径

# 训练超参数（针对 RTX 4060 8G 优化）
BATCH_SIZE = 8                # 实际批大小
GRADIENT_ACCUMULATION_STEPS = 4  # 累积梯度，使有效批大小 = 6 * 4 = 32
LEARNING_RATE = 6e-5
NUM_EPOCHS = 4
MAX_SEQ_LENGTH = 256         # 文本截断长度，分类任务 256 通常足够
LABEL_SMOOTHING = 0.1        # 关键：为获得平滑概率矩阵必须设置 > 0

# 推理时温度系数（软化概率分布）
TEMPERATURE = 2.0

# 交叉验证折数
CV_FOLDS = 5

# 硬件配置
USE_FP16 = True              # 混合精度训练，必须开启以节省显存
USE_GRADIENT_CHECKPOINT = False  # 若显存仍不足可设为 True，但会降低速度