import numpy as np
import torch
import json
from sklearn.model_selection import cross_val_predict

def mlp_calc_proba(mlp_model, device, x_fused, y, class_names):

    mlp_model.eval()
    with torch.no_grad():
        x_tensor = torch.tensor(x_fused, dtype=torch.float32).to(device)
        logits = mlp_model(x_tensor)
        proba = torch.softmax(logits, dim=1).cpu().numpy()

    return build_matrix(proba, y, class_names, "affinity_matrix.json")

def rf_calc_proba(rf_clf, x_fused, y, class_names):
    proba = cross_val_predict(
        rf_clf,
        x_fused,
        y,
        cv=5,
        method='predict_proba',
        n_jobs=-1
    ) # 使用 cross_val_predict 获取每个样本的预测概率
    return build_matrix(proba, y, class_names)

def build_matrix(proba, y, class_names, save_path=None):
    n_classes = len(class_names)  # 类别数（或者叫节点数）
    affinity_matrix = np.zeros((n_classes, n_classes))  # 初始化一个空矩阵

    for i in range(n_classes):
        mask = (y == i)
        if np.any(mask):
            affinity_matrix[i] = proba[mask].mean(axis=0)
    # 对于每个类别 i，找出所有标签为 i 的样本（mask）
    # 对这些样本的预测概率向量（proba[mask]）按列取平均，得到一个长度为 n_classes 的平均概率向量
    # 将平均概率向量赋值给 affinity_matrix[i]，表示从类别 i 出发，预测为其他类别的平均概率

    affinity_matrix = (affinity_matrix + affinity_matrix.T) / 2  # 上述操作得到的是不对称矩阵，通过取平均使其对称化，得到无向的亲缘强度

    if save_path is not None:
        save_affinity_to_json(affinity_matrix, class_names, save_path)

    return affinity_matrix

def save_affinity_to_json(affinity_matrix, class_names, file_path):
    # 确保 class_names 是 Python 原生字符串列表
    if isinstance(class_names, np.ndarray):
        class_names = class_names.tolist()          # 如果是 numpy 数组，转为列表
    else:
        class_names = [str(name) for name in class_names]  # 强制转换为字符串

    data = {
        'class_names': class_names,
        'affinity_matrix': affinity_matrix.tolist()
    }

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"亲和矩阵已保存至: {file_path}")

def load_affinity_matrix(file_path):
    """
    从 JSON 文件加载亲和矩阵与类别名。

    Parameters
    ----------
    file_path : str
        JSON 文件路径

    Returns
    -------
    affinity_matrix : np.ndarray
        加载后的亲和矩阵
    class_names : list of str
        类别名称列表
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    affinity_matrix = np.array(data['affinity_matrix'])
    class_names = data['class_names']

    print(f"亲和矩阵已从 {file_path} 加载，形状: {affinity_matrix.shape}")
    return affinity_matrix, class_names