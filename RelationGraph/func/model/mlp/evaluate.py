from RelationGraph.func.model.mlp.train import JobDataset
from RelationGraph.func.utils.calc_top_k import top_k_accuracy

import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, f1_score


# 增强版 MLP 预测评估函数
def mlp_predict_and_evaluate(model, device, x_test, y_test=None, verbose=True, batch_size=32, top_k_list=None):
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

#--- temp ---#

def predict_proba_dict(model, x_sample, device, class_names):
    """
    使用训练好的 MLP 模型对**单条数据**进行概率预测，返回 {分类: 概率} 字典。

    参数:
        model (MLPClassifier): 已经训练完成的模型（get_mlp 或 get_mlp_cross 返回的对象）
        x_sample (np.ndarray / list / torch.Tensor): **单条数据的特征向量**
            - 形状必须是 (input_dim,)，与训练时的 x_fused 维度完全一致
            - 注意：如果你输入的是原始字符串（职位描述等），请先用训练时相同的特征提取方式
              （如 TF-IDF + embedding 融合）把它转换成数值特征向量 x_sample，再传入本函数。
        device (torch.device): 推理设备（如 torch.device('cpu') 或 torch.device('cuda')）
        class_names (List[str], 可选): 类别名称列表（顺序必须与训练时的 y 一致）。
            如果不传，则默认使用 "class_0", "class_1", ...

    返回:
        Dict[str, float]: {分类名称: 概率}，概率之和为 1.0

    示例用法（假设你已经准备好特征向量）:
        # x_new = ...  # 用训练时的特征提取逻辑把字符串转成 numpy array
        result = predict_proba_dict(model, x_new, device, class_names=['数据分析师', '产品经理', '软件工程师'])
        print(result)
        # 输出示例: {'数据分析师': 0.78, '产品经理': 0.15, '软件工程师': 0.07}
    """
    # 1. 模型切换到评估模式
    model.eval()

    # 2. 把单条特征转为 tensor 并增加 batch 维度 (1, input_dim)
    if isinstance(x_sample, np.ndarray):
        x_tensor = torch.from_numpy(x_sample.astype(np.float32)).unsqueeze(0).to(device)
    elif isinstance(x_sample, list):
        x_tensor = torch.tensor(x_sample, dtype=torch.float32).unsqueeze(0).to(device)
    elif isinstance(x_sample, torch.Tensor):
        x_tensor = x_sample.unsqueeze(0).to(device) if x_sample.dim() == 1 else x_sample.to(device)
    else:
        raise TypeError("x_sample 必须是 np.ndarray、list 或 torch.Tensor")

    # 3. 前向推理 + softmax 得到概率
    with torch.no_grad():
        logits = model(x_tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    # 4. 构造类别名称（如果用户没提供）
    if class_names is None:
        class_names = [f"class_{i}" for i in range(len(probs))]

    # 5. 构建最终字典
    result = {}
    for i in range(len(probs)):
        class_name = str(class_names[i])
        result[class_name] = float(probs[i])

    return result