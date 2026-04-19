from RelationGraph.func.utils.get_model import get_embedding_temp

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from datasets import Dataset, DatasetDict
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
import numpy as np
import pandas as pd
import re

def calc_embedding(txt):
    """对文本列表进行嵌入计算，返回 (n_samples, dim) 的 numpy 数组"""
    embedding = get_embedding_temp()
    embeddings_vec = embedding.embed_documents(txt)
    return np.array(embeddings_vec, dtype=np.float32)

def init_data(df):
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

    def to_str_if_list(x):
        if isinstance(x, list):
            # 如果列表非空，取第一个元素；否则返回空字符串
            return str(x[0]) if x else ''
        return str(x) if x is not None else ''

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

def init_data_raw(df):
    """
    将所有相关列合并为自然语言文本，直接进行嵌入计算，
    返回纯文本嵌入矩阵 (n_samples, embedding_dim)
    """

    def format_all_fields_to_text(row):
        """
        将一行招聘数据的多个字段拼接成一段完整的中文描述
        """
        parts = []

        # 1. 薪资范围
        salary = row.get('薪资范围', '')
        if pd.notna(salary) and str(salary).strip() != '':
            parts.append(f"薪资范围为{str(salary).strip()}。")

        # 2. 公司规模
        size = row.get('公司规模', '')
        if pd.notna(size) and str(size).strip() != '':
            parts.append(f"公司规模为{str(size).strip()}。")

        # 3. 所属行业（可能包含逗号分隔的多个标签）
        industry = row.get('所属行业', '')
        if pd.notna(industry) and str(industry).strip() != '':
            # 将逗号替换为顿号，使其更符合中文阅读习惯
            industry_str = str(industry).replace(',', '、')
            parts.append(f"所属行业包括{industry_str}。")

        # 4. 公司类型（同样处理多标签）
        company_type = row.get('公司类型', '')
        if pd.notna(company_type) and str(company_type).strip() != '':
            type_str = str(company_type).replace(',', '、')
            parts.append(f"公司类型为{type_str}。")

        # 5. 地址
        address = row.get('地址', '')
        if pd.notna(address) and str(address).strip() != '':
            parts.append(f"工作地点位于{str(address).strip()}。")

        # 6. 岗位详情（原始文本）
        detail = row.get('岗位详情', '')
        if pd.notna(detail) and str(detail).strip() != '':
            parts.append(f"岗位详细描述：{str(detail).strip()}")

        # 用空格连接所有非空片段
        return " ".join(parts)

    # 为每行生成融合文本
    df['combined_text'] = df.apply(format_all_fields_to_text, axis=1)

    # 过滤掉完全空白的文本行（可选）
    df = df[df['combined_text'].str.strip() != '']

    text_list = df['combined_text'].tolist()

    # 计算文本嵌入
    text_embeddings = calc_embedding(text_list)

    print(f"最终融合特征维度: {text_embeddings.shape[1]}")
    return text_embeddings

#--- 分割线 ---#

def init_data_lora(df, init_type = 'raw'):

    # print(df.columns)  # 显示所有列名

    def generate_description(row):
        """
        根据行数据生成职位描述文本
        """
        parts = []

        def format_field(value, empty_text="无"):
            """
            将字段值格式化为友好的字符串表示，处理缺失情况。
            如果 value 是列表，则过滤掉空值后用中文顿号 、 连接元素；若列表为空，返回 empty_text（默认"无"）。
            如果 value 是标量（字符串或数值），空值返回 empty_text，否则直接转字符串。
            """
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

        # 提取列值并用format_field转化
        salary = row.get("薪资范围", "未知")
        education = row.get("学历要求", "未知")
        promotion = row.get("晋升路径", "未知")
        parts.append(f"薪资范围为{salary}，学历要求{education}，晋升路径为{promotion}。")

        company = format_field(row.get("公司"), "未提供")
        parts.append(f"所在公司：{company}。")

        qualities = format_field(row.get("综合素质"), "无特殊要求")
        parts.append(f"需要具备的综合素质：{qualities}。")

        skills = format_field(row.get("职业技能"), "无特殊要求")
        parts.append(f"需要掌握的职业技能：{skills}。")

        certs = format_field(row.get("证书"), "无")
        parts.append(f"需要持有的证书：{certs}。")

        tasks = format_field(row.get("工作内容"), "未描述")
        parts.append(f"主要工作内容：{tasks}。")

        majors = format_field(row.get("专业"), "不限")
        parts.append(f"专业要求：{majors}。")

        experience = format_field(row.get("工作经验"), "不限")
        parts.append(f"工作经验要求：{experience}。")

        industry = format_field(row.get("行业"), "未知行业")
        parts.append(f"所属行业：{industry}。")

        # print(" ".join(parts))
        return " ".join(parts)

    if init_type == 'raw': # 用原始的数据，只进行简单清洗
        df = df[['职业类别', '岗位详情']].dropna()
        df.columns = ['label', 'text']
    elif init_type == 'graph': # 用从知识图谱上摘下来的数据拼出来的数据
        df['text'] = df.apply(generate_description, axis=1) # 把多个列并到 "text" 列
        df = df[['职业类别', 'text']].dropna() # 只保留这两列
        df.rename(columns={'职业类别': 'label'}, inplace=True) # 改名

    le = LabelEncoder() # LabelEncoder 实例
    df['label_id'] = le.fit_transform(df['label']) # 调用fit_transform

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