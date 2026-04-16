from RelationGraph.func.utils.get_model import get_embedding_temp

from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
import numpy as np
import pandas as pd
import re

def calc_embedding(texts):
    """
    对文本列表进行嵌入计算，返回嵌入向量数组。
    """
    embeddings = get_embedding_temp()
    embeddings_vec = embeddings.embed_documents(texts)
    return np.array(embeddings_vec, dtype=np.float32)

def parse_salary_range(salary_str):
    """
    匹配模式：数字-数字，中间可能含空格，后面可选"元每月"或"每月"
    """
    pattern = r'(\d+)\s*-\s*(\d+)\s*(?:元)?每月'
    match = re.search(pattern, salary_str.strip())
    if match:
        try:
            v1 = float(match.group(1))
            v2 = float(match.group(2))
            return (v1 + v2) / 2.0
        except:
            return np.nan
    return np.nan

def init_data(df):
    """
    对给定的 DataFrame 进行特征工程，返回融合后的特征矩阵 X_fused。
    输入 df 必须包含以下列：
        - 薪资范围（str 或 list）
        - 学历要求（str 或 list）
        - 晋升路径（str 或 list）
        - 综合素质（list of str）
        - 职业技能（list of str）
        - 证书（list of str）
        - 工作内容（list of str）
        - 专业（list of str）
        - 工作经验（list of str）
        - 行业（list of str）
    """

    def to_str_if_list(x):
        if isinstance(x, list):
            # 如果列表非空，取第一个元素；否则返回空字符串
            return str(x[0]) if x else ''
        return str(x) if x is not None else ''

    str_columns = ['薪资范围', '学历要求', '晋升路径']
    for col in str_columns:
        if col in df.columns:
            df[col] = df[col].apply(to_str_if_list)

    # Step 1：处理薪资范围（数值特征）
    df['薪资平均值'] = df['薪资范围'].apply(parse_salary_range)
    salary_median = df['薪资平均值'].median()
    df['薪资平均值'] = df['薪资平均值'].fillna(salary_median) # 避免 ChainedAssignmentError：直接赋值而非 inplace

    numeric_features = df[['薪资平均值']].values.astype(np.float32)
    scaler = StandardScaler()
    numeric_scaled = scaler.fit_transform(numeric_features)

    # Step 2：处理学历要求、晋升路径（文本嵌入）
    df['edu_promo_text'] = (
        df['学历要求'].fillna('').astype(str) + ' ' +
        df['晋升路径'].fillna('').astype(str)
    )
    texts = df['edu_promo_text'].tolist()
    text_embeddings = calc_embedding(texts)

    # Step 3：处理多值列表列（Multi-hot 编码）
    multi_cols = ['综合素质', '职业技能', '证书', '工作内容', '专业', '工作经验', '行业']

    def clean_list(lst):
        """将列表元素统一转为字符串，并过滤空值/无效占位符"""
        if not isinstance(lst, list):
            return []
        cleaned = []
        for item in lst:
            s = str(item).strip()
            # 过滤掉空字符串、'nan'、'None' 等无效标记
            if s and s.lower() not in ('nan', 'none', ''):
                cleaned.append(s)
        return cleaned

    # 替换原来的循环部分
    for col in multi_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_list)
        else:
            df[col] = [[] for _ in range(len(df))]

    multi_hot_parts = []
    for col in multi_cols:
        mlb = MultiLabelBinarizer()
        encoded = mlb.fit_transform(df[col])
        multi_hot_parts.append(encoded)
        print(f"列 '{col}' 编码后维度: {encoded.shape[1]}")

    multi_hot_combined = np.hstack(multi_hot_parts)

    # Step 4: 融合所有特征
    x_fused = np.hstack([
        text_embeddings,
        numeric_scaled,
        multi_hot_combined
    ])

    print(f"最终融合特征维度: {x_fused.shape[1]}")
    return x_fused

