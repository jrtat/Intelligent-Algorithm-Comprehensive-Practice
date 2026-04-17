from RelationGraph.func.classification import mlp_calc_proba, rf_calc_proba, xgboost_calc_proba
from RelationGraph.func.get_data import get_data, get_data_raw
from RelationGraph.func.preprocess import init_data, init_data_nli
from RelationGraph.func.get_result import build_matrix
from RelationGraph.func.evaluate import evaluate_proba

import torch
from sklearn.preprocessing import LabelEncoder

# Step 0：初始化模型 与 读取数据
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') # 检测是否有gpu，如果有就用cuda
print(f"使用设备: {device}")
# df = get_data()
df = get_data_raw()
# 得到的df有以下列：
'''
[岗位id, 薪资范围, 学历要求, 晋升路径, 职业类别, 公司, 综合素质, 职业技能, 证书, 工作内容, 专业, 工作经验, 行业]
'''

# Step 1：处理数据
print("Step 1")
X_fused = init_data(df)
# X_fused = init_data_nli(df)
# X_fused = init_data_nli_raw(df)
le = LabelEncoder() # 使用 LabelEncoder 将原始岗位名称（字符串）转换为整数标签 y（0, 1, 2, …）
y = le.fit_transform(df['职业类别'])
class_names = le.classes_ # 保存编码器中的类别列表 class_names，用于后续映射

# Step 2：训练分类器 并 得到分类结果 （三选一）
print("Step 2")
# proba1 = mlp_calc_proba(device, X_fused, y) # 用MLP分类
# proba2 = rf_calc_proba(X_fused, y) # 用RandomForest分类
proba3 = xgboost_calc_proba(X_fused, y) # 用XGBoost分类

# Step 3：构建岗位亲缘关系矩阵
print("Step 3")
# affinity_matrix1 = build_matrix(proba1, y, class_names)
# affinity_matrix2 = build_matrix(proba2, y, class_names)
affinity_matrix3 = build_matrix(proba3, y, class_names)

# Step 4：评估效果
# 对已有的三个概率矩阵进行评估
print("\n===== 分类器性能评估 =====")
# evaluate_proba(proba1, y, "MLP")
# evaluate_proba(proba2, y, "RandomForest")
evaluate_proba(proba3, y, "XGBoost")

# Example
print("Step 4")
# print(get_similar_occupations("C/C++", class_names, affinity_matrix1))
# print(get_similar_occupations("C/C++", class_names, affinity_matrix2))
# print(get_similar_occupations("Java", class_names, affinity_matrix3))