# 知识图谱构建


## 知识图谱构建

### 实体

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

### 关系

岗位 --需要--> 技能

岗位 --需要--> 证书

岗位 --涉及--> 企业 

岗位 --涉及--> 行业

# 附录

## 什么是GraphRAG

[RAG中的Embedding模型](https://www.bilibili.com/video/BV19RJhzyEWN/?vd_source=e2b79f6eccec7953cc61b1c113da15ca)

[GraphRAG的图结构（知识图谱）](https://www.bilibili.com/video/BV1tsYPztEiE) B站自带AI字幕效果不错

[GraphRAG中，文本如何被转换成图上的节点和边](https://www.bilibili.com/video/BV1zoKuzoENM)

## 采用哪个模型将文本转为图谱

[LLMGraphTransformer](https://cloud.tencent.com/developer/article/2638663) （[原文](https://medium.com/data-science/building-knowledge-graphs-with-llm-graph-transformer-a91045c49b59)）



