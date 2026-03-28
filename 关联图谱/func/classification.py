import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict
from xgboost import XGBClassifier
from tqdm import tqdm

class JobDataset(Dataset): # 将特征矩阵和标签转换为 PyTorch 张量，提供标准的数据集接口，便于 DataLoader 使用
    def __init__(self, X_fused, y):
        self.X = torch.tensor(X_fused, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class MLPClassifier(nn.Module):
    def __init__(self, input_dim, num_classes, hidden_dim=1024):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), # 第一层 Hidden层 默认有 hidden_dim 个节点
            nn.ReLU(), # 激活函数
            nn.Dropout(0.3), # 在训练时，以 0.3 的概率随机“丢弃”当前层的部分神经元（将其输出置为 0），防止神经元之间产生复杂的共适应关系，从而抑制过拟合
            nn.Linear(hidden_dim, hidden_dim // 2), # 第二层 Hidden层 节点数相较于第一层减半
            nn.ReLU(), # 激活函数
            nn.Dropout(0.3), # 同上
            nn.Linear(hidden_dim // 2, num_classes) # 第三层 Output层
        )

    def forward(self, x):
        return self.net(x)

def train_mlp(device,X_fused, y, num_epochs, batch_size, learning_rate):

    # Step 0：数据处理
    dataset = JobDataset(X_fused, y) # 输入格式转换
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    # 使用 DataLoader 将数据集包装为可迭代对象
    # 每个迭代会返回一个小批量（batch_x, batch_y）

    # Step 1：配置模型
    model = MLPClassifier(input_dim=X_fused.shape[1], num_classes=len(np.unique(y))).to(device) # 实例化 MLPClassifier 模型
    # 使用 .to(device) 将模型参数移动到指定设备
    criterion = nn.CrossEntropyLoss()
    # 定义损失函数：交叉熵损失，适用于多分类问题
    optimizer = optim.Adam(model.parameters(), lr = learning_rate)
    # 使用 Adam 优化器，传入模型的所有可训练参数，并设置学习率 lr

    # Step 2：训练模型
    model.train() # 将模型设置为训练模式。这会启用 Dropout 层并保持 BatchNorm 层的统计信息更新
    for epoch in range(num_epochs):
        total_loss = 0 # 用于累计当前 epoch 所有批次的损失总和
        for batch_x, batch_y in tqdm(loader, desc=f"Epoch {epoch+1}/{num_epochs}"): # tqdm 显示进度条，desc 设置描述信息
            batch_x, batch_y = batch_x.to(device), batch_y.to(device) # 将当前批次的特征和标签移动到模型所在的设备
            optimizer.zero_grad() # 清空上一批次的梯度信息
            logits = model(batch_x) # 前向传播：将当前批次的特征输入模型，得到模型输出的 logits，形状为 (batch_size, num_classes)
            loss = criterion(logits, batch_y) # 计算损失：将模型输出的 logits 和真实标签传入交叉熵损失函数，得到当前批次的损失值
            loss.backward() # 反向传播：根据损失值计算每个模型参数的梯度
            optimizer.step() # 更新模型参数：优化器根据计算出的梯度对参数进行一次更新，即执行一步梯度下降
            total_loss += loss.item() # 将当前批次的损失值累加到 total_loss 中
        print(f"Epoch {epoch+1} 平均损失: {total_loss/len(loader):.4f}")

    # Step 4：用模型计算并返回结果
    return model

def mlp_calc_proba(device, X_fused):
    mlp_model = train_mlp(device, X_fused, y, num_epochs=60, batch_size=64, learning_rate=1e-3)

    mlp_model.eval()
    with torch.no_grad():
        X_tensor = torch.tensor(X_fused, dtype=torch.float32).to(device)
        logits = mlp_model(X_tensor)
        proba = torch.softmax(logits, dim=1).cpu().numpy()
    return proba

def rf_calc_proba(X_fused,y):
    rf_clf = RandomForestClassifier(
        n_estimators=300,  # 树的数量
        max_depth=25,  # 最大深度
        min_samples_leaf=2,
        class_weight='balanced',  # 处理类别不平衡
        random_state=42,
        n_jobs=-1  # 使用所有CPU核心
    )

    proba = cross_val_predict(
        rf_clf,
        X_fused,
        y,
        cv=5,
        method='predict_proba',
        n_jobs=-1
    ) # 使用 cross_val_predict 获取每个样本的预测概率

    return proba

def XGBoost_calc_proba(X_fused,y):

    xgb_clf = XGBClassifier(
        n_estimators=300,
        max_depth=25,
        learning_rate=0.1,  # XGBoost 特有的学习率
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        eval_metric='mlogloss'
    )

    proba = cross_val_predict(
        xgb_clf,
        X_fused,
        y,
        cv=5,
        method='predict_proba',
        n_jobs=-1
    )

    return proba
