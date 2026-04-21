import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score
from tqdm import tqdm
import copy

class JobDataset(Dataset):
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
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim // 2, num_classes)
        )

    def forward(self, x):
        return self.net(x)

def get_mlp(device,
            x_train, y_train,
            num_epochs=100,
            batch_size=64,
            learning_rate=1e-3,
            hidden_dim=1024):
    """
    训练 MLP 模型（无验证集，无早停，训练全部 epoch 后返回最终模型）。

    参数:
        device (torch.device): 计算设备
        X_train (np.ndarray): 训练特征矩阵
        y_train (np.ndarray): 训练标签
        num_epochs (int): 训练轮数
        batch_size (int): 批次大小
        learning_rate (float): 学习率
        hidden_dim (int): 第一隐藏层维度

    返回:
        model (MLPClassifier): 训练完成后的模型
    """
    # 创建数据集与加载器
    train_dataset = JobDataset(x_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # 模型、损失函数、优化器
    input_dim = x_train.shape[1]
    num_classes = len(np.unique(y_train))
    model = MLPClassifier(input_dim, num_classes, hidden_dim=hidden_dim).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(num_epochs):
        # 训练阶段
        model.train()
        total_loss = 0.0
        for batch_x, batch_y in tqdm(train_loader, desc=f"Epoch {epoch + 1}/{num_epochs} [Train]", leave=False):
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg_train_loss = total_loss / len(train_loader)

        print(f"Epoch {epoch + 1:3d} | Train Loss: {avg_train_loss:.4f}")

    print("训练完成，返回最终模型。")
    return model

def get_mlp_advance(device,
                    x_train, y_train,
                    x_val, y_val,
                    num_epochs=100,
                    batch_size=64,
                    learning_rate=1e-3,
                    hidden_dim=1024,
                    patience=10):
    """
    训练 MLP 模型，使用验证集监控并返回最佳模型。
    """
    # 创建数据集与加载器
    train_dataset = JobDataset(x_train, y_train)
    val_dataset = JobDataset(x_val, y_val)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # 模型、损失函数、优化器
    input_dim = x_train.shape[1]
    num_classes = len(np.unique(y_train))
    model = MLPClassifier(input_dim, num_classes, hidden_dim=hidden_dim).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    best_val_acc = 0.0
    best_model_wts = copy.deepcopy(model.state_dict())
    epochs_no_improve = 0

    for epoch in range(num_epochs):
        # 训练阶段
        model.train()
        total_loss = 0.0
        for batch_x, batch_y in tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs} [Train]", leave=False):
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg_train_loss = total_loss / len(train_loader)

        # 验证阶段
        model.eval()
        val_loss = 0.0
        val_preds, val_targets = [], []
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                logits = model(batch_x)
                loss = criterion(logits, batch_y)
                val_loss += loss.item()
                preds = torch.argmax(logits, dim=1)
                val_preds.extend(preds.cpu().numpy())
                val_targets.extend(batch_y.cpu().numpy())
        avg_val_loss = val_loss / len(val_loader)
        val_acc = accuracy_score(val_targets, val_preds)

        print(f"Epoch {epoch+1:3d} | Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val Acc: {val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_wts = copy.deepcopy(model.state_dict())
            epochs_no_improve = 0
            print(f"  --> 新的最佳模型 (Val Acc = {val_acc:.4f})")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"早停触发，在 epoch {epoch+1} 停止训练。")
                break

    model.load_state_dict(best_model_wts)
    print(f"训练完成，最佳验证准确率: {best_val_acc:.4f}")
    return model