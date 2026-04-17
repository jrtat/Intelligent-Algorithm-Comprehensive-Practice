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

def init_data_nli(df):
    """
    将招聘数据的各列拼接成适合 RoBERTa 输入的单个文本段落。

    参数:
        df: 包含以下列的 DataFrame
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

    返回:
        texts: 每行拼接后的字符串列表，可直接送入 tokenizer。
    """

    def to_str(x):
        """将任意类型安全地转换为字符串，处理列表、数组和缺失值"""
        # 先处理容器类型（列表、元组、numpy 数组）
        if isinstance(x, (list, tuple, np.ndarray)):
            cleaned = []
            for item in x:
                # 跳过缺失值
                if pd.isna(item):
                    continue
                s = str(item).strip()
                if s:  # 过滤空字符串
                    cleaned.append(s)
            return "、".join(cleaned) if cleaned else ""

        # 处理标量缺失值（None, np.nan, pd.NA 等）
        if pd.isna(x):
            return ""

        # 普通标量值转字符串并去空格
        s = str(x).strip()
        return s if s else ""

    # 逐列处理并构建文本段落
    text_parts = []

    # 1. 基本信息（数值/单值字段）
    if '薪资范围' in df.columns:
        text_parts.append("薪资范围：" + df['薪资范围'].apply(to_str))

    if '学历要求' in df.columns:
        text_parts.append("学历要求：" + df['学历要求'].apply(to_str))

    if '工作经验' in df.columns:
        text_parts.append("工作经验：" + df['工作经验'].apply(to_str))

    # 2. 技能与素质（列表字段）
    if '职业技能' in df.columns:
        text_parts.append("职业技能：" + df['职业技能'].apply(to_str))

    if '综合素质' in df.columns:
        text_parts.append("综合素质：" + df['综合素质'].apply(to_str))

    if '证书' in df.columns:
        text_parts.append("证书要求：" + df['证书'].apply(to_str))

    # 3. 专业与工作内容（列表字段）
    if '专业' in df.columns:
        text_parts.append("专业要求：" + df['专业'].apply(to_str))

    if '工作内容' in df.columns:
        text_parts.append("工作内容：" + df['工作内容'].apply(to_str))

    # 4. 职业发展与行业背景
    if '晋升路径' in df.columns:
        text_parts.append("晋升路径：" + df['晋升路径'].apply(to_str))

    if '行业' in df.columns:
        text_parts.append("所属行业：" + df['行业'].apply(to_str))

    # 将所有部分用句号分隔，形成完整段落
    # 注意：若某部分为空字符串，拼接后会出现连续句号，但模型对轻微冗余不敏感
    combined_series = text_parts[0]
    for part in text_parts[1:]:
        combined_series = combined_series + "。" + part

    # 转换为列表返回
    texts = combined_series.tolist()
    print("\n" + "=" * 60)
    print("拼接后的文本示例：")
    print("=" * 60)
    for i, text in enumerate(texts[:10], 1):
        print(f"\n【样本 {i}】")
        print(text)
        print("-" * 60)

    # 同时输出原始数据中前3行对应列的简要信息，便于对照
    print("\n原始数据的部分字段（用于对照）：")
    print(df[['薪资范围', '学历要求', '工作经验']].head(10).to_string())
    print("=" * 60 + "\n")
    return texts