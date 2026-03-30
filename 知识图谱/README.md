# 知识图谱构建

## 思路

用之前处理好的文本来构建graphRAG，结果存储在Neo4j中，并设置graph_retriever函数，use_llm函数。
在后续使用大模型时把问题打包发给use_llm，该函数会调用graph_retriever在Neo4j上查询与话题相关的内容，将其打包给LLM，以提高LLM的回答能力。
其中graph_retriever采用混合查询的方式，既使用向量的方式检索，也使用图的方式检索。

## 节点&边类型的设置

#### 节点

- 岗位名称（约100种）
  - 工资情况（月薪最小、月薪最大、平均月薪、四分位数）
  - 学历分布
  - 创新，沟通，抗压，能力要求（平均值？）
  - 对实习时间要求的分布
  - 垂直职业发展方向（集合）
  - 城市分布

- 行业
  - 在GB/T 4754-2017所属的门类

- 公司
  - 企业规模
  - 企业类型
  - 公司发展情况
  - 企业描述（非结构化文本）

- 证书

- 技能

#### 关系

岗位 --需要--> 技能

岗位 --需要--> 证书

岗位 --涉及--> 企业 

岗位 --涉及--> 行业

## 文件结构

```
graphRAG
├── func
│   ├── build_graphRAG.py
│   └── use_graphRAG.py
└── main.py
```

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

