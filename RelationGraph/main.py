from RelationGraph.func.other.get_data import get_data,get_data_raw
from RelationGraph.func.other.preprocess import init_data, init_data_raw, init_data_lora
from RelationGraph.func.train.rf.train import get_rf, rf_evaluate, rf_predict_proba
from RelationGraph.func.train.mpl.train import get_mlp,mlp_evaluate,mlp_predict_proba
from RelationGraph.func.other.get_result import mlp_calc_proba

import torch
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

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
# init_data_lora(df, init_type= "not raw")

le = LabelEncoder() # 使用 LabelEncoder 将原始岗位名称（字符串）转换为整数标签 y（0, 1, 2, …）
y = le.fit_transform(df['职业类别'])
class_names = le.classes_ # 保存编码器中的类别列表 class_names，用于后续映射
# 先分出 80% 训练，20% 临时集（验证+测试）
X_train, X_temp, y_train, y_temp = train_test_split(
    X_fused, y, test_size=0.2, random_state=42, stratify=y
)
# 再将临时集均分为验证和测试（各10%）
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

'''
rf_clf = get_rf(X_train, y_train)
rf_proba = rf_predict_proba(rf_clf, X_test)
rf_evaluate(rf_proba, y_test)
'''

mlp_clf = get_mlp(device, X_train, y_train, X_val, y_val)
mlp_proba = mlp_predict_proba(mlp_clf, device, X_test)
mlp_evaluate(mlp_proba, y_test)

mlp_calc_proba(mlp_clf, device, X_fused, y, class_names)

'''
# Step 2：训练分类器 并 得到分类结果 （三选一）
print("Step 2")
proba1 = mlp_calc_proba(device, X_fused, y) # 用MLP分类
proba2 = rf_calc_proba(X_fused, y) # 用RandomForest分类
proba3 = xgboost_calc_proba(X_fused, y) # 用XGBoost分类

# Step 3：构建岗位亲缘关系矩阵
print("Step 3")
affinity_matrix1 = build_matrix(proba1, y, class_names)
affinity_matrix2 = build_matrix(proba2, y, class_names)
affinity_matrix3 = build_matrix(proba3, y, class_names)

# Step 4：评估效果
# 对已有的三个概率矩阵进行评估
print("\n===== 分类器性能评估 =====")
evaluate_proba(proba1, y, "MLP")
evaluate_proba(proba2, y, "RandomForest")
# evaluate_proba(proba3, y, "XGBoost")
'''
