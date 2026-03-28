from func.vectorization import init_data
from func.classification import train_mlp, mlp_calc_proba, rf_calc_proba, XGBoost_calc_proba

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder
import networkx as nx
import matplotlib.pyplot as plt

# Step 0：初始化模型 与 读取数据
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') # 检测是否有gpu，如果有就用cuda
print(f"使用设备: {device}")
df = pd.read_excel('processed.xlsx', header=0)

# Step 1：处理数据
X_fused = init_data(df)
le = LabelEncoder() # 使用 LabelEncoder 将原始岗位名称（字符串）转换为整数标签 y（0, 1, 2, …）
y = le.fit_transform(df['岗位名称'])
class_names = le.classes_ # 保存编码器中的类别列表 class_names，用于后续映射

# Step 2：训练分类器 并 得到分类结果 （三选一）
# proba = mlp_calc_proba(device, X_fused) # 用MLP分类
# proba = rf_calc_proba(X_fused, y) # 用RandomForest分类
proba = XGBoost_calc_proba(X_fused, y) # 用XGBoost分类

# Step 3：构建岗位亲缘关系矩阵
n_classes = len(class_names) # 类别数（或者叫节点数）
affinity_matrix = np.zeros((n_classes, n_classes)) # 初始化一个空矩阵

for i in range(n_classes):
    mask = (y == i)
    if mask.sum() > 0:
        affinity_matrix[i] = proba[mask].mean(axis=0)
# 对于每个类别 i，找出所有标签为 i 的样本（mask）
# 对这些样本的预测概率向量（proba[mask]）按列取平均，得到一个长度为 n_classes 的平均概率向量
# 将平均概率向量赋值给 affinity_matrix[i]，表示从类别 i 出发，预测为其他类别的平均概率

affinity_matrix = (affinity_matrix + affinity_matrix.T) / 2 # 上述操作得到的是不对称矩阵，通过取平均使其对称化，得到无向的亲缘强度

# 非必要 Step 4：构建 NetworkX 并 可视化
G = nx.Graph()
for name in class_names:
    G.add_node(name)

threshold = 0.005   # 设置阈值
edge_count = 0
for i in range(n_classes):
    for j in range(i + 1, n_classes):
        weight = affinity_matrix[i, j]
        if weight > threshold: # 便利关联矩阵，高于阈值才认为有关联
            G.add_edge(class_names[i], class_names[j], weight=weight)
            edge_count += 1

print(f"关系图谱构建完成！节点数: {len(G.nodes())}, 边数: {edge_count}")

plt.figure(figsize=(22, 22))
pos = nx.spring_layout(G, k=0.55, iterations=60, seed=1) # 使用 spring_layout（Fruchterman-Reingold 算法）计算节点位置
# k：节点间斥力强度，值越大节点越分散。
# iterations：迭代次数，确保布局稳定。
# seed=1：固定随机种子，保证结果可重现。

degrees = dict(G.degree()) # 获取每个节点的度（连接的边数）
node_sizes = [degrees[node] * 100 for node in G.nodes()] # 节点大小按度缩放，度越大节点越大（乘以 100 调整视觉效果）
edge_weights = [G[u][v]['weight'] * 20 for u, v in G.edges()] # 提取每条边的权重，并乘以 20 作为边的线宽，使权重更大的边更粗

nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='lightblue', alpha=0.9) # 绘制节点
nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.6, edge_color='gray') # 绘制边
nx.draw_networkx_labels(G, pos, font_size=9, font_family='SimHei') # 绘制标签

plt.title("岗位亲缘关系图谱（Sentence-Transformer + MLP + Multi-Hot）", fontsize=16) # 添加标题
plt.axis('off') # 关闭坐标轴
plt.tight_layout() # 调整布局
plt.savefig('job_affinity_graph_sentence_transformer.png', dpi=300, bbox_inches='tight') # 保存为图片

# 非必要 Step 5：输出前20

print("\n=== Top 20 最强亲缘关系 ===")
edges_sorted = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)[:20]
for u, v, data in edges_sorted:
    print(f"{u}  <-->  {v}    亲缘强度: {data['weight']:.4f}")

print("\n=== RandomForest 版本运行完成 ===")
