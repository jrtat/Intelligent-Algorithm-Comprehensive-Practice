# 知识图谱构建

总地来说，这部分代码只需离线单独执行，不需要运行在后端。这部分负责把原始数据转换成知识图谱并存入Neo4j，并添加向量索引并分块，以作为GraphRAG使用。


(以下是旧版，不作数)

# 知识图谱构建

## 思路

用之前处理好的文本来构建graphRAG，结果存储在Neo4j中。

## 节点&边类型的设置

#### 节点



#### 关系



---

## 文件结构

```
graphRAG
├── func
│   ├── utils
│   │   ├── get_models.py （提供初始化模型的函数，主要是llm和embedding）
│   │   ├── conn_neo4j.py （提供连接图数据库相关的函数）
│   │   ├── graphsearcher.py （提供图搜索相关的函数）
│   ├── extract_document.py （从Excel中提取每一行，转成一段话，用于后续提取知识图谱）
│   ├── build_graphrag.py （init负责构建知识图谱，deduplication负责节点去重）
│   ├── get_retriver.py （获取混合检索器，尚未完工）
│   └── use_graphrag.py （使用知识图谱增强llm的能力，尚未完工）
└── init.py （调用get_extracted_document，init和deduplication完成知识图谱的构建工作）
```

extract_document.py：把Excel文档转成文本列表

build_graphRAG.py：最核心的部分，包含init函数（负责把文本转成图，存入Neo4j，并初始化hybrid_retriever）以及graph_retriever函数

use_graphRAG.py：包含use_llm函数

main.py：只是一个简单的使用示例

## 算法选择与参数配置

### 文本转为图谱的模型选择与配置


### Embedding算法的选择与参数配置


### Neo4jVector的配置


# 附录

## 什么是GraphRAG

[RAG中的Embedding模型](https://www.bilibili.com/video/BV19RJhzyEWN/?vd_source=e2b79f6eccec7953cc61b1c113da15ca)

[GraphRAG的图结构（知识图谱）](https://www.bilibili.com/video/BV1tsYPztEiE) B站自带AI字幕效果不错

[GraphRAG中，文本如何被转换成图上的节点和边](https://www.bilibili.com/video/BV1zoKuzoENM)

## 什么是LLMGraphTransformer

[LLMGraphTransformer](https://cloud.tencent.com/developer/article/2638663) （[原文](https://medium.com/data-science/building-knowledge-graphs-with-llm-graph-transformer-a91045c49b59)）

## 什么是混合检索（hybrid_retriever）

## 模型调用测试代码

```python

import os
from langchain_openai import OpenAIEmbeddings
from numpy.linalg import norm
import numpy as np

embeddings = OpenAIEmbeddings(
    model="qwen3-embedding:8b",
    base_url="http://59.72.63.156:14138/v1",  # 自定义端点
    api_key="Empty",
    dimensions=1536,
    tiktoken_enabled=False,
    check_embedding_ctx_length=False
)

documents = [
    "机器学习是人工智能的一个分支",
    "深度学习使用多层神经网络",
    "今天是晴天"
]
doc_vecs = embeddings.embed_documents(documents)

print(doc_vecs)
print(len(doc_vecs))

llm = ChatOpenAI(
    model="qwen3:8b",  # 模型名字（xjx实验室）
    base_url="http://59.72.63.156:14138/v1", # url（xjx实验室）
    api_key="EMPTY",  # vLLM 不需要真实 key
    temperature=0  # 温度0 = 输出最稳定（对于提取图谱这个应用来说，0是最好的，不要调这个参数）
)
response = llm.invoke("你好，请介绍一下自己")
print(response.content)

```



