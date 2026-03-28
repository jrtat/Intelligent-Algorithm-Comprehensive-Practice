import numpy as np
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
from sentence_transformers import SentenceTransformer

def Sentence_Transformer(df):
    text_embeddings = st_model.encode(
        df['combined_text'].tolist(),  # 将合并后的文本列转换为 Python 列表并作为输入
        convert_to_numpy=True,  # 返回 NumPy 数组而非张量
        show_progress_bar=True,  # 显示进度条
        batch_size=32  # 一次处理 32 条文本，平衡内存与速度
    )  # 调用 Sentence‑Transformer 模型的 encode 方法，将文本转换为嵌入向量
    return text_embeddings

def init_data(df):

    # Step 0：模型准备
    model_name = "paraphrase-multilingual-mpnet-base-v2"  # Sentence-Transformer 模型，中文效果优秀的模型
    st_model = SentenceTransformer(model_name) # 实例化该模型，加载预训练权重到内存，用于后续将文本转换为语义嵌入

    # Step 1：把编号（所属行业、公司类型） 转成 multi-hot 矩阵
    all_industry = set()
    for industry in df['所属行业']:
        all_industry.update(industry)
    all_development = set()
    for development in df['公司类型']:
        all_development.update(development) # 收集所有的 行业 和 公司类型 （集合的形式）

    industry_list = sorted(list(all_industry))
    development_list = sorted(list(all_development)) # 将集合转成列表

    mlb_industry = MultiLabelBinarizer(classes=industry_list)
    mlb_development = MultiLabelBinarizer(classes=development_list) # 用于将多标签列表转换为 multi-hot矩阵
    # MultiLabelBinarizer 是 sklearn 提供的工具

    industry_multi_hot = mlb_industry.fit_transform(df['所属行业'])
    development_multi_hot = mlb_development.fit_transform(df['公司类型']) # 根据提供的列表，将对应列的每个多标签列表转换为一个向量
    # 输出为一个 (样本数, len(industry_list)) 的 NumPy 数组

    # Step 2：文本合并（地址 + 岗位详情）
    text_cols = ['地址', '岗位详情']
    df['combined_text'] = df[text_cols].fillna('').agg(' '.join, axis=1) # 把文本合成一句话

    # Step 3：计算岗位文本嵌入（二选一）
    text_embeddings = Sentence_Transformer(df)

    # Step 4：提取数值列（薪资范围、公司规模）并标准化
    numeric_cols = ['薪资范围', '公司规模']

    scaler = StandardScaler() # 用于将数值特征标准化（减去均值，除以标准差），使每个特征均值为 0，方差为 1，消除量纲影响
    numeric_features = scaler.fit_transform(df[numeric_cols].values) # 提取数值列的值（假设已经是数值类型），转换为 NumPy 数组

    # Step 5：最终融合特征
    X_fused = np.hstack([
        text_embeddings,  # Sentence-Transformer 语义向量
        numeric_features,  # 标准化后的薪资 + 公司规模
        industry_multi_hot,  # 行业 multi-hot
        development_multi_hot  # 公司类型 multi-hot
    ])

    print(f"最终融合特征维度: {X_fused.shape[1]}")

    return X_fused



