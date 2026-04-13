# 关联图谱构建

## 思路

在对数据进行清洗之后将其当作标注数据来看（岗位名称即为标注值y，其余行作为特征值X），这促使我们想到了监督学习这个方向。

Excel中的列（清洗后）可分为以下三类：
1. 纯数值，无需过多处理标准化后可以直接拿来用
2. 文本，需要通过Embedding算法将其转成向量
3. 编号，比如所在行业，可以将他们转换成编号，用Multi-Hot来存

之后采用常用监督学习算法（神经网络，随机森林等）即可

## 文件结构

```
relationship_graph
├── func
│   ├── vectorlization.py
│   └── classification.py
└── main.py
```

vectorlization.py：把Excel中的列（清洗后）合并，作为训练的输入，返回X_fused（特征）

classification.py：分类算法的实现，返回model（训练好的模型）

main.py：通过调用以上两个文件中的函数，实现整个流程

## 算法选择与参数配置

### Embedding算法的选择与参数配置

- 本地测试时：轻量化模型Sentence‑Transformer，下载库后可以直接使用

- 最终选择：Qwen3-Embedding-8B


### 分类算法选择与参数配置

- 选择1：MPL分类器

- 选择2：RandomForest分类器

- 选择3：XGboost分类器

# 附录
