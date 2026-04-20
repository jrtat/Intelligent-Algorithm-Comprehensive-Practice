import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, f1_score

class JobDataset(Dataset): # 将特征矩阵和标签转换为 PyTorch 张量，提供标准的数据集接口，便于 DataLoader 使用
    def __init__(self, x_fused, y):
        self.X = torch.tensor(x_fused, dtype=torch.float32)
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

def get_mlp(x_train, y_train, device=None, num_epochs=20, batch_size=128, learning_rate=1e-3):
    """
    训练 MLP 模型

    参数:
        x_train (np.ndarray): 训练特征矩阵
        y_train (np.ndarray): 训练标签
        device (str, optional): 计算设备 ('cuda' 或 'cpu')，默认为自动检测
        num_epochs (int): 训练轮数
        batch_size (int): 批次大小
        learning_rate (float): 学习率

    返回:
        model (MLPClassifier): 训练好的 MLP 模型
    """
    # 自动检测设备
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # 数据处理
    dataset = JobDataset(x_train, y_train)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # 配置模型
    input_dim = x_train.shape[1]
    num_classes = len(np.unique(y_train))
    model = MLPClassifier(input_dim=input_dim, num_classes=num_classes).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # 训练循环
    model.train()
    for epoch in range(num_epochs):
        total_loss = 0
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        print(f"Epoch {epoch+1}/{num_epochs} | 平均损失: {avg_loss:.4f}")

    return model


def mlp_predict_proba(model, x_test, device=None):
    """
    使用训练好的 MLP 模型计算测试集的预测概率

    参数:
        model (MLPClassifier): 训练好的 MLP 模型
        x_test (np.ndarray): 测试特征矩阵
        device (str, optional): 计算设备，默认自动检测

    返回:
        proba (np.ndarray): 预测概率矩阵，形状为 (样本数, 类别数)
    """
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    model.eval()
    model.to(device)

    # 转换为张量并移动到设备
    x_tensor = torch.tensor(x_test, dtype=torch.float32).to(device)

    with torch.no_grad():
        logits = model(x_tensor)
        proba = torch.softmax(logits, dim=1).cpu().numpy()

    return proba


def mlp_evaluate(proba_mlp_test, y_test):
    """
    基于预测概率计算并打印 MLP 模型的评估指标

    参数:
        proba_mlp_test (np.ndarray): 预测概率矩阵
        y_test (np.ndarray): 真实标签
    """
    pred_mlp_test = np.argmax(proba_mlp_test, axis=1)
    mlp_acc = accuracy_score(y_test, pred_mlp_test)
    mlp_f1 = f1_score(y_test, pred_mlp_test, average='macro')
    print(f"MLP 测试集结果 | Accuracy: {mlp_acc:.4f} | Macro F1: {mlp_f1:.4f}")