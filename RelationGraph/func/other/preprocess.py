from RelationGraph.func.utils.get_model import get_embedding_temp

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from datasets import Dataset, DatasetDict
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
import numpy as np
import pandas as pd
import re

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

#--- 分割线 ---#

def calc_embedding(texts):
    """对文本列表进行嵌入计算，返回 (n_samples, dim) 的 numpy 数组"""
    embedding = get_embedding_temp()
    embeddings_vec = embedding.embed_documents(texts)
    return np.array(embeddings_vec, dtype=np.float32)

def parse_salary(salary_str):
    """将 '3000-4000' 转换为 3500，若无法转换返回 NaN"""
    import re
    if pd.isna(salary_str):
        return np.nan
    salary_str = str(salary_str).strip()
    # 处理 '面议' 等非数字情况
    if '面议' in salary_str or salary_str == '':
        return np.nan
    # 提取数字
    numbers = re.findall(r'\d+\.?\d*', salary_str)
    if not numbers:
        return np.nan
    # 如果有两个数字（如 '3000-4000'），取平均值
    if len(numbers) >= 2:
        low = float(numbers[0])
        high = float(numbers[1])
        return (low + high) / 2
    else:
        return float(numbers[0])

def parse_company_size(size_str):
    """将 '20-99人' 转换为人数数值（取区间平均值），无法转换返回 NaN"""
    import re
    if pd.isna(size_str):
        return np.nan
    size_str = str(size_str).strip()
    # 常见范围：'20-99人'、'500-999人'、'10000人以上'
    numbers = re.findall(r'\d+', size_str)
    if not numbers:
        return np.nan
    if len(numbers) >= 2:
        low = float(numbers[0])
        high = float(numbers[1])
        return (low + high) / 2
    else:
        # '1000-9999人' 可能被识别为两个数字，但上面的逻辑已覆盖
        return float(numbers[0])

def init_data_raw(df):
    # 1. 处理缺失值，将行业和公司类型转换为列表格式
    def split_tags(x):
        if isinstance(x, str):
            return [tag.strip() for tag in x.split(',') if tag.strip()]
        else:
            return []

    df['所属行业_list'] = df['所属行业'].apply(split_tags)
    df['公司类型_list'] = df['公司类型'].apply(split_tags)

    # 2. 收集所有出现的标签
    all_industry = set()
    for tags in df['所属行业_list']:
        all_industry.update(tags)
    all_development = set()
    for tags in df['公司类型_list']:
        all_development.update(tags)

    industry_list = sorted(list(all_industry))
    development_list = sorted(list(all_development))

    # 3. 转换为 multi-hot 矩阵
    mlb_industry = MultiLabelBinarizer(classes=industry_list)
    mlb_development = MultiLabelBinarizer(classes=development_list)
    industry_multi_hot = mlb_industry.fit_transform(df['所属行业_list'])
    development_multi_hot = mlb_development.fit_transform(df['公司类型_list'])

    # 4. 文本合并（地址 + 岗位详情）
    text_cols = ['地址', '岗位详情']
    df['combined_text'] = df[text_cols].fillna('').agg(' '.join, axis=1)

    # 5. 计算文本嵌入
    text_list = df['combined_text'].tolist()
    # print(f"待编码文本数量: {len(text_list)}")
    text_embeddings = calc_embedding(text_list)

    # 6. 数值特征处理：先解析薪资和公司规模为数值，再标准化
    df['薪资数值'] = df['薪资范围'].apply(parse_salary)
    df['规模数值'] = df['公司规模'].apply(parse_company_size)

    # 处理缺失值（填充为该列中位数）
    df['薪资数值'] = df['薪资数值'].fillna(df['薪资数值'].median())
    df['规模数值'] = df['规模数值'].fillna(df['规模数值'].median())

    numeric_cols = ['薪资数值', '规模数值']
    scaler = StandardScaler()
    numeric_features = scaler.fit_transform(df[numeric_cols].values)

    # 7. 拼接所有特征
    x_fused = np.hstack([
        text_embeddings,
        numeric_features,
        industry_multi_hot,
        development_multi_hot
    ])

    print(f"最终融合特征维度: {x_fused.shape[1]}")
    return x_fused

def ensure_list(val):
    """确保值是列表，用于多值字段处理"""
    if isinstance(val, list):
        return val
    if val is None:
        return []
    return [val]

def format_field(value, empty_text="无"):
    """将字段值格式化为字符串：列表用'、'连接，标量直接转字符串，空值返回 empty_text"""
    if isinstance(value, list):
        if not value:  # 空列表
            return empty_text
        # 过滤掉 None 或空字符串元素，并用顿号连接
        valid_items = [str(v) for v in value if v not in (None, "")]
        return "、".join(valid_items) if valid_items else empty_text
    else:
        if value is None or value == "":
            return empty_text
        return str(value)

def generate_description(row):
    """根据行数据生成职位描述文本"""
    parts = []

    # 岗位基本信息
    salary = row.get("薪资范围", "未知")
    education = row.get("学历要求", "未知")
    promotion = row.get("晋升路径", "未知")

    parts.append(f"薪资范围为{salary}，学历要求{education}，晋升路径为{promotion}。")

    # 公司
    company = format_field(row.get("公司"), "未提供")
    parts.append(f"所在公司：{company}。")

    # 综合素质
    qualities = format_field(row.get("综合素质"), "无特殊要求")
    parts.append(f"需要具备的综合素质：{qualities}。")

    # 职业技能
    skills = format_field(row.get("职业技能"), "无特殊要求")
    parts.append(f"需要掌握的职业技能：{skills}。")

    # 证书
    certs = format_field(row.get("证书"), "无")
    parts.append(f"需要持有的证书：{certs}。")

    # 工作内容
    tasks = format_field(row.get("工作内容"), "未描述")
    parts.append(f"主要工作内容：{tasks}。")

    # 专业
    majors = format_field(row.get("专业"), "不限")
    parts.append(f"专业要求：{majors}。")

    # 工作经验
    experience = format_field(row.get("工作经验"), "不限")
    parts.append(f"工作经验要求：{experience}。")

    # 行业
    industry = format_field(row.get("行业"), "未知行业")
    parts.append(f"所属行业：{industry}。")

    # print(" ".join(parts))
    return " ".join(parts)

def init_data_lora(df, init_type = 'raw'):

    print(df.columns)  # 输出 Index 对象，显示所有列名

    if init_type == 'raw':
        df = df[['职业类别', '岗位详情']].dropna()
        df.columns = ['label', 'text']
    else:
        df['text'] = df.apply(generate_description, axis=1)
        df = df[['职业类别', 'text']].dropna()
        df.rename(columns={'职业类别': 'label'}, inplace=True)

    # 标签编码
    le = LabelEncoder()
    df['label_id'] = le.fit_transform(df['label'])

    # 划分训练/验证/测试 (8:1:1)
    train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label_id'])
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['label_id'])

    # 保存为 HuggingFace Dataset 格式
    dataset = DatasetDict({
        'train': Dataset.from_pandas(train_df[['text', 'label_id']]),
        'validation': Dataset.from_pandas(val_df[['text', 'label_id']]),
        'test': Dataset.from_pandas(test_df[['text', 'label_id']])
    })

    dataset.save_to_disk('./func/train/lora/job_classify_dataset')