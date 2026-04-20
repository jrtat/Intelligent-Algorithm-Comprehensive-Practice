from RelationGraph.func.train.mpl.train import JobDataset
from RelationGraph.func.utils.calc_top_k import top_k_accuracy

import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, f1_score


# 增强版 MLP 预测评估函数
def mlp_predict_and_evaluate(model, device, x_test, y_test=None, verbose=True, batch_size=64, top_k_list=None):
    """
    使用训练好的 MLP 模型对测试集进行概率预测，若提供 y_test 则评估并打印结果。
    若同时提供 top_k_list，则额外计算并打印 Top-k 准确率。

    参数:
        model (nn.Module): 训练好的 PyTorch 模型
        device (torch.device): 计算设备
        x_test (np.ndarray): 测试特征矩阵
        y_test (np.ndarray, optional): 测试标签，若提供则计算并打印准确率与 Macro F1
        verbose (bool): 是否打印评估结果（当 y_test 不为 None 时生效）
        batch_size (int): 推理时的批次大小
        top_k_list (tuple or list, optional): 如 (1, 3, 5)，计算对应 Top-k 准确率

    返回:
        若 y_test 不为 None 且 top_k_list 不为 None，返回 (proba, topk_dict)
        否则返回 proba (np.ndarray)
    """
    model.eval()
    # 构建临时数据集（标签占位，不影响预测）
    dataset = JobDataset(x_test, np.zeros(len(x_test)))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    all_probs = []
    with torch.no_grad():
        for batch_x, _ in loader:
            batch_x = batch_x.to(device)
            logits = model(batch_x)
            probs = torch.softmax(logits, dim=1)
            all_probs.append(probs.cpu().numpy())
    proba = np.vstack(all_probs)

    if y_test is not None:
        pred = np.argmax(proba, axis=1)
        acc = accuracy_score(y_test, pred)
        f1 = f1_score(y_test, pred, average='macro')
        if verbose:
            print(f"MLP 测试集结果 | Accuracy: {acc:.4f} | Macro F1: {f1:.4f}")
        if top_k_list is not None:
            topk = top_k_accuracy(proba, y_test, top_k_list)
            if verbose:
                for k, v in topk.items():
                    print(f"Top-{k} Accuracy: {v:.4f}")
            return proba, topk
    return proba