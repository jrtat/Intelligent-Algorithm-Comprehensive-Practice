from RelationGraph.func.utils.get_model import get_embedding_temp

from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
import numpy as np
import pandas as pd
import re

def calc_embedding(txt): # 文本列表的Embedding计算，返回 (n_samples, dim) 的 numpy 数组
    embedding = get_embedding_temp()
    embeddings_vec = embedding.embed_documents(txt)
    return np.array(embeddings_vec, dtype=np.float32)

def init_data_graph(df):
    """
    接收get_data处理的数据，返回融合后的特征矩阵 X_fused。
    输入 df 必须包含以下列：
        - 公司 （str）           不使用
        - 薪资范围（str 或 list） 转成数值
        - 晋升路径（list of str） 取列表的首值
        - 学历要求（list of str） 取列表的首值
        - 综合素质（list of str） Multi-hot 编码
        - 职业技能（list of str） Multi-hot 编码
        - 证书   （list of str） Multi-hot 编码
        - 工作内容（list of str） Multi-hot 编码
        - 专业   （list of str） Multi-hot 编码
        - 工作经验（list of str） Multi-hot 编码
        - 行业   （list of str） Multi-hot 编码
    """

    def to_str_if_list(x):  # 如果列表非空，取第一个元素；否则返回空字符串
        if isinstance(x, list):
            return str(x[0]) if x else ''
        return str(x) if x is not None else ''

    def parse_salary_range(salary_str): # 匹配模式：数字-数字，中间可能含空格，后面可选"元每月"或"每月
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

    # Step 2：处理学历要求、晋升路径（Embedding）
    df['edu_promo_text'] = (
        df['学历要求'].fillna('').astype(str) + ' ' +
        df['晋升路径'].fillna('').astype(str)
    )
    texts = df['edu_promo_text'].tolist()
    text_embeddings = calc_embedding(texts)

    # Step 3：处理多值列表列（Multi-hot 编码）
    multi_cols = ['综合素质', '职业技能', '证书', '工作内容', '专业', '工作经验', '行业']

    def clean_list(lst): # 将列表元素统一转为字符串，并过滤空值/无效占位符
        if not isinstance(lst, list):
            return []
        cleaned = []
        for item in lst:
            s = str(item).strip()
            # 过滤掉空字符串、'nan'、'None' 等无效标记
            if s and s.lower() not in ('nan', 'none', ''):
                cleaned.append(s)
        return cleaned

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

def init_data_raw(df, if_lora = False):

    def format_all_fields_to_text(row):  # 将一行招聘数据的多个字段拼接成一段完整的中文描述
        parts = []

        salary = row.get('薪资范围', '')  # 薪资范围
        if pd.notna(salary) and str(salary).strip() != '':
            parts.append(f"该岗位的薪资范围为{str(salary).strip()}。")

        company = row.get('公司名称', '')  # 公司类型
        if pd.notna(company) and str(company).strip() != '':
            parts.append(f"所属公司为{company}。")

        size = row.get('公司规模', '')  # 公司规模
        if pd.notna(size) and str(size).strip() != '':
            parts.append(f"公司规模为{str(size).strip()}。")

        industry = row.get('所属行业', '')  # 所属行业
        if isinstance(industry, list):  # 如果 industry 是列表，先转为用顿号分隔的字符串
            industry = '、'.join(str(item).strip() for item in industry if str(item).strip())
        if industry:  # 二次确认非空
            parts.append(f"所属行业包括{str(industry).strip()}。")

        company_type = row.get('公司类型', '')  # 公司类型
        if pd.notna(company_type) and str(company_type).strip() != '':
            parts.append(f"公司类型为{company_type}。")

        address = row.get('地址', '')  # 地址
        if pd.notna(address) and str(address).strip() != '':
            parts.append(f"工作地点位于{str(address).strip()}。")

        detail = row.get('岗位详情', '')  # 岗位详情
        if pd.notna(detail) and str(detail).strip() != '':
            parts.append(f"岗位详细描述：{str(detail).strip()}")

        return " ".join(parts)  # 用空格连接所有上述片段

    # Step 1：为每行生成融合文本
    df['combined_text'] = df.apply(format_all_fields_to_text, axis=1)

    # Step 2：过滤掉完全空白的文本行（可选）
    df = df[df['combined_text'].str.strip() != '']

    # Step 3：计算文本嵌入
    if not if_lora:
        text_list = df['combined_text'].tolist()
        text_embeddings = calc_embedding(text_list)

        print(f"最终融合特征维度: {text_embeddings.shape[1]}")
        return text_embeddings
    else:
        return df


