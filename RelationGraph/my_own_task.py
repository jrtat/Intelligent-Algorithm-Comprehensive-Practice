from RelationGraph.func.prepare.get_data import get_data_raw
from RelationGraph.func.prepare.init_data import init_data_raw
from RelationGraph.func.train.rf.train import get_rf, rf_evaluate, rf_predict_proba
from RelationGraph.func.train.mpl.train import get_mlp, mlp_evaluate, mlp_predict_proba
from RelationGraph.func.use.get_result import mlp_calc_proba, rf_calc_proba

import torch
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Step 0：初始化模型 与 读取数据
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') # 检测是否有gpu，如果有就用cuda
print(f"使用设备: {device}")
# df = get_data()
df = get_data_raw()

# Step 1：处理数据
print("Step 1")
# X_fused = init_data_graph(df)
X_fused = init_data_raw(df)

le = LabelEncoder() # 使用 LabelEncoder 将原始岗位名称（字符串）转换为整数标签 y（0, 1, 2, …）
y = le.fit_transform(df['职业类别'])
class_names = le.classes_ # 保存编码器中的类别列表 class_names，用于后续映射
# 先分出 90% 训练，10% 临时集（验证+测试）
X_train, X_temp, y_train, y_temp = train_test_split(
    X_fused, y, test_size=0.1, random_state=42, stratify=y
)
# 再将临时集均分为验证和测试（各5%）
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

# Step 2： 训练模型并评估

#--- rf ---#
'''
rf_clf = get_rf(X_train, y_train)
rf_proba = rf_predict_proba(rf_clf, X_test)
rf_evaluate(rf_proba, y_test)

rf_calc_proba(rf_clf, X_fused, y, class_names)
'''
#--- mlp ---#

mlp_clf = get_mlp(device, X_train, y_train, X_val, y_val)
mlp_proba = mlp_predict_proba(mlp_clf, X_test, device)
mlp_evaluate(mlp_proba, y_test)

mlp_calc_proba(mlp_clf, device, X_fused, y, class_names)




