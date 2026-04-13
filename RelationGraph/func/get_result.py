import numpy as np
from typing import List, Dict, Union

def build_matrix(proba, y, class_names):
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
    return affinity_matrix

def get_similar_occupations(occupation_name: str,
                            class_names: np.ndarray,
                            affinity_matrix: np.ndarray) -> List[Dict[str, Union[str, float]]]:
    """
    计算某个职业类别与其他所有职业类别的相似度，并按降序返回排序结果。

    Parameters
    ----------
    occupation_name : str
        目标职业类别的名称，必须在 `class_names` 中存在。
    class_names : np.ndarray
        由 `LabelEncoder.classes_` 获得的所有职业类别名称数组。
    affinity_matrix : np.ndarray
        职业亲缘矩阵，形状为 (n_classes, n_classes)，对称矩阵。

    Returns
    -------
    List[Dict[str, Union[str, float]]]
        排序后的相似度列表，每个元素为字典，包含：
        - "职业类型": 类别名称 (str)
        - "相似度评分": 相似度值 (float)
    """
    # 检查输入名称是否在类别列表中
    if occupation_name not in class_names:
        raise ValueError(f"职业类别 '{occupation_name}' 不存在于 class_names 中。")

    # 获取目标类别的索引
    idx = np.where(class_names == occupation_name)[0][0]

    # 提取该类别与其他所有类别的相似度向量
    similarity_vector = affinity_matrix[idx]

    # 构建（索引，相似度）列表，排除自身
    similarities = []
    for i, (name, score) in enumerate(zip(class_names, similarity_vector)):
        if i != idx:  # 不包含自身
            similarities.append({"职业类型": name, "相似度评分": float(score)})

    # 按相似度评分降序排序
    similarities_sorted = sorted(similarities, key=lambda x: x["相似度评分"], reverse=True)

    return similarities_sorted