import numpy as np

def top_k_accuracy(proba, y_true, k_list=(1, 3, 5)):
    """
    计算 Top-k 准确率：只要真实类别出现在预测概率最高的 k 个类别中即视为正确。

    参数:
        proba (np.ndarray): 预测概率矩阵，形状 (n_samples, n_classes)
        y_true (np.ndarray): 真实标签，形状 (n_samples,)
        k_list (tuple or list): 需要计算的 k 值序列

    返回:
        dict: 键为 k，值为对应的 Top-k 准确率
    """
    proba = np.asarray(proba)
    y_true = np.asarray(y_true)

    n_samples = proba.shape[0]
    n_classes = proba.shape[1]

    # 获取每个样本概率从高到低的类别索引排序
    top_indices = np.argsort(proba, axis=1)[:, ::-1]

    # 真实标签扩展为列向量，便于与 top_indices 的每一列比较
    y_true_expanded = y_true.reshape(-1, 1)

    results = {}
    for k in k_list:
        if k > n_classes:
            acc = 1.0
        else:
            correct = np.any(top_indices[:, :k] == y_true_expanded, axis=1)
            acc = np.mean(correct)
        results[k] = acc

    return results