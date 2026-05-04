from RelationGraph.func.utils.config import model_name, model_path
from RelationGraph.func.utils.calc_matrix import build_matrix   # 假设路径可访问

import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from peft import PeftModel

# 预存标签
id2label = {
    0: "APP推广", 1: "BD经理", 2: "C/C++", 3: "Java", 4: "产品专员/助理", 5: "储备干部",
    6: "储备经理人", 7: "内容审核", 8: "前端开发", 9: "咨询顾问", 10: "售后客服",
    11: "商务专员", 12: "培训师", 13: "大客户代表", 14: "实施工程师", 15: "广告销售",
    16: "律师", 17: "律师助理", 18: "总助/CEO助理/董事长助理", 19: "技术支持工程师", 20: "招聘专员/助理",
    21: "日语翻译", 22: "档案管理", 23: "法务专员/助理", 24: "测试工程师", 25: "游戏推广",
    26: "游戏运营", 27: "猎头顾问", 28: "电话客服", 29: "电话销售", 30: "知识产权/专利代理",
    31: "硬件测试", 32: "社区运营", 33: "科研人员", 34: "管培生/储备干部", 35: "统计员",
    36: "网络客服", 37: "网络销售", 38: "英语翻译", 39: "质检员", 40: "质量管理/测试",
    41: "资料管理", 42: "软件测试", 43: "运营助理/专员", 44: "销售助理", 45: "销售工程师",
    46: "销售运营", 47: "项目专员/助理", 48: "项目招投标", 49: "项目经理/主管", 50: "风电工程师"
}

# 配置路径
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载 tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 加载基础模型
base_model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=51,
    torch_dtype=torch.bfloat16,
    ignore_mismatched_sizes=True
)

# 加载 LoRA 适配器
model = PeftModel.from_pretrained(base_model, model_path)
model.to(DEVICE)
model.eval()

def predict_probabilities(text):
    """
    对单个文本进行分类，返回类别名称到概率的字典。
    """
    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt"
    ).to(DEVICE)

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1).squeeze(0).cpu().float().numpy()

    return {id2label[idx]: float(prob) for idx, prob in enumerate(probs)}

def lora_calc_proba(texts, y, batch_size = 32):  # 使用 LoRA 微调模型计算文本集合的预测概率，并构建类别间亲缘矩阵

    # Step 1：声明全局变量 把模型转为评估模式
    global tokenizer, model, id2label
    model.eval()
    n_samples = len(texts)
    n_classes = len(id2label)

    # Step 2：按索引顺序生成类别名称列表
    class_names = [id2label[i] for i in range(n_classes)]

    # Step 3：调用模型进行评估
    all_probs = []
    with torch.no_grad():
        for i in range(0, n_samples, batch_size):
            batch_texts = texts[i:i+batch_size]
            inputs = tokenizer(
                batch_texts,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            ).to(DEVICE)

            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).cpu().float().numpy()
            all_probs.append(probs)

    proba = np.concatenate(all_probs, axis=0)          # shape: (n_samples, n_classes)
    y = np.asarray(y)                                  # 确保为 numpy 数组

    # Step 4：调用build_matrix，保存亲缘矩阵（并返回）
    return build_matrix(proba, y, class_names, save_path="affinity_matrix_lora.json")
