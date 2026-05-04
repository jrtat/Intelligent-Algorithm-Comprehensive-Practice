from src.RelationGraph.func.model.mlp.train import JobDataset
from src.RelationGraph.func.utils.calc_top_k import top_k_accuracy

import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, f1_score


def mlp_predict_and_evaluate(model, device, x_test, y_test=None, verbose=True, batch_size=32, top_k_list=None):

    # Step 1：把模型设置为评估模式
    model.eval()
    
    # Step 2：构建临时数据集
    dataset = JobDataset(x_test, np.zeros(len(x_test)))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    # Step 3：评估
    all_probs = []
    with torch.no_grad():
        for batch_x, _ in loader:
            batch_x = batch_x.to(device)
            logits = model(batch_x)
            probs = torch.softmax(logits, dim=1)
            all_probs.append(probs.cpu().numpy())
    proba = np.vstack(all_probs)

    # Step 4： 计算Top-k
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

    # Step 5： 返回预测结果
    return proba

#--- temp ---#

def predict_proba_dict(model, x_sample, device, class_names):
    # Step 1：模型切换到评估模式
    model.eval()

    # Step 2：把单条特征转为 tensor 并增加 batch 维度 (1, input_dim)
    if isinstance(x_sample, np.ndarray):
        x_tensor = torch.from_numpy(x_sample.astype(np.float32)).unsqueeze(0).to(device)
    elif isinstance(x_sample, list):
        x_tensor = torch.tensor(x_sample, dtype=torch.float32).unsqueeze(0).to(device)
    elif isinstance(x_sample, torch.Tensor):
        x_tensor = x_sample.unsqueeze(0).to(device) if x_sample.dim() == 1 else x_sample.to(device)
    else:
        raise TypeError("x_sample 必须是 np.ndarray、list 或 torch.Tensor")

    # Step 3：前向推理 + softmax 得到概率
    with torch.no_grad():
        logits = model(x_tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    # Step 4：构造类别名称（如果用户没提供）
    if class_names is None:
        class_names = [f"class_{i}" for i in range(len(probs))]

    # Step 5：构建最终字典
    result = {}
    for i in range(len(probs)):
        class_name = str(class_names[i])
        result[class_name] = float(probs[i])

    return result
