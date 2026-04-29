from RelationGraph.func.utils.config import personal_model_path1, personal_model_path2

from RelationGraph.func.prepare.get_data import get_data_raw, get_data_graph
from RelationGraph.func.prepare.init_data import init_data_raw, init_data_graph
from RelationGraph.func.model.mlp.train import get_mlp, get_mlp_cross
from RelationGraph.func.model.mlp.evaluate import mlp_predict_and_evaluate
# from RelationGraph.func.use.get_result import mlp_calc_proba, rf_calc_proba

import torch
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Step 0：初始化模型 与 读取数据
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') # 检测是否有gpu，如果有就用cuda
print(f"使用设备: {device}")
# df = get_data_graph()
df = get_data_raw()

# Step 1：处理数据（多数内容只需执行一次，因为处理1w条数据大概有个10分钟左右，不方便测试，所以存起来）
# X_fused = init_data_graph(df)
# X_fused = init_data_raw(df)
# np.save("X_fused.npy", X_fused) # 保存为 .npy 文件（精确二进制格式，保留 dtype 和 shape）

X_fused = np.load("X_fused.npy") # 读出数据
le = LabelEncoder() # 使用 LabelEncoder 将原始岗位名称（字符串）转换为整数标签 y（0, 1, 2, …）
y = le.fit_transform(df['职业类别'])
class_names = le.classes_ # 保存编码器中的类别列表 class_names，用于后续映射
# 先分出 90% 训练，10% 临时集（验证+测试）

X_train, X_temp, y_train, y_temp = train_test_split(
    X_fused, y, test_size=0.1, random_state= 42, stratify=y
)

# 再将临时集均分为验证和测试（各5%）
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

# Step 2： 训练模型 & 评估模型 & 保存模型
#--- mlp：多层感知机 ---#
mlp_clf = get_mlp_cross(device, X_train, y_train, X_val, y_val)
mlp_predict_and_evaluate(mlp_clf, device, x_test= X_test, y_test= y_test, top_k_list= [1,2,3])
save_dict1 = {
    'model_state_dict': mlp_clf.state_dict(),
    'input_dim': mlp_clf.net[0].in_features,      # 从模型中获取输入维度
    'num_classes': mlp_clf.net[-1].out_features,   # 最后一层输出维度
    'hidden_dim': mlp_clf.net[0].out_features,     # 第一隐藏层维度（与定义时一致）
}

torch.save(save_dict1, personal_model_path1)

#--- mlp_all：这个比较特殊，其使用全部数据训练，并使用全部数据测试 ---#
mlp_all_clf = get_mlp( device=device, x_train=X_fused, y_train=y)
mlp_predict_and_evaluate(mlp_all_clf, device, x_test=X_fused, y_test=y, top_k_list=[1, 2, 3])
save_dict2 = {
    'model_state_dict': mlp_all_clf.state_dict(),
    'input_dim': mlp_all_clf.net[0].in_features,      # 从模型中获取输入维度
    'num_classes': mlp_all_clf.net[-1].out_features,   # 最后一层输出维度
    'hidden_dim': mlp_all_clf.net[0].out_features,     # 第一隐藏层维度（与定义时一致）
}

torch.save(save_dict2, personal_model_path2)