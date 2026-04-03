# utils（工具）

## ExcelMaker

- 将数据打包成excel形式。
- 如果有列表形式，将自动转化成用逗号隔开的字符串。

> ### **Job**列名如下：
> | 列名          | 描述 |
> |-------------|----|
> | id          | 岗位编号 |
> | name        | 岗位名称 |
> | company     | 公司名称 |
> | description | 岗位描述 |
> | source      |    |
> | education_1 |  |
> | education_2 |  |
> | 创新能力        |  |
> | 抗压能力        |  |
> | 沟通能力        |  |
> | 学习能力        |  |
> | 实习能力        |  |
> | 职业技能        |  |
> | 证书要求        |  |

### 使用方法：
1. 创建一个ExcelMaker对象，file_name为保存地址。
2. save_job(data)能将data字典转化为DataFrame形式，最后保存为excel文件。


## FileProcessor
- 掌管文件的读写处理。
- 实现数据类到json格式的转换。
- 实现从储存类的字典一键转换到json格式保存到文件的操作。

### 使用方法：
1. 创建一个FileProcessor对象，file_name为保存地址。
2. read()和write(data)操作为简单的读写操作。
3. converter(obj)为内在的格式转换器，可递归使用。
4. save(data)一键将复杂的数据类型存储为json格式的文件。

## LLMInvoker

- LLM调用器，调用LLM模型。
- 可内置base_url和api_key。
- *目前使用本地的ollama架构的模型。*

> ### 本地可使用模型如下（部分模型无法正常使用未列出）：
> | 模型名称                     | 描述                 |
> |--------------------------|--------------------|
> | qwen3:8b                 | 最稳定，最快，最轻量         |
> | qwen3:14b                | 稳定，但速度较慢           |
> | qwen3.5:9b               | 设备较老，勉强能跑          |
> | qwen3.5:27b              | 不太能跑               |
> | qwen3.5:cloud            | 云模型，有限额，几乎顶配       |
> | qwen3-embedding:8b       | 语言向量模型，适合分析相似度等特征使用 |
> | glm-4.7-flash:latest     | Openclaw默认下的，不知道效果 |
> | qwen3-coder:30b          | 适合写代码，不适合跑数据       |
> | qwen3-coder-next:latest  | 同上，且硬件需求高          |


### 使用方法：
1. 创建一个LLMInvoker对象，base_url为模型地址，model_name指定模型名称。
2. 有内置的_call_ollama(prompt, stream)函数调用模型，stream为是否返回流式数据，默认为False。
3. *暂时使用extract_job_key_info(job_description)来实现数据处理，后续考虑是否拆分到processor处理*
4. *暂时使用batch_extract_job_info(jobs_dict, save_path)来实现大模型调用的批量化处理，后续考虑是否单开一个类实现批处理的可塑性处理。（就是看怎样批处理或者是不批处理好）*
