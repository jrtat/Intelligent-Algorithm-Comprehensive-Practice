from RelationGraph.func.utils.get_model import get_embedding_temp

from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from typing import List
import re

# 假设 get_embedding_temp() 已在其他地方定义，返回 LangChain 嵌入模型实例
# from your_embedding_module import get_embedding_temp

def calc_embedding(texts: List[str]):
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

def init_data(df: pd.DataFrame):
    """
    对给定的 DataFrame 进行特征工程，返回融合后的特征矩阵 X_fused。
    输入 df 必须包含以下列：
        - 薪资范围（str）
        - 学历要求（str）
        - 晋升路径（str）
        - 综合素质（list of str）
        - 职业技能（list of str）
        - 证书（list of str）
        - 工作内容（list of str）
        - 专业（list of str）
        - 工作经验（list of str）
        - 行业（list of str）
    职业类别作为标签单独处理，不参与特征融合。
    """

    # Step 1：处理薪资范围（数值特征）
    df['薪资平均值'] = df['薪资范围'].apply(parse_salary_range)
    salary_median = df['薪资平均值'].median() # 计算中位数
    df['薪资平均值'].fillna(salary_median, inplace=True) # 若存在缺失值，可用中位数填充（根据实际情况调整）

    numeric_features = df[['薪资平均值']].values.astype(np.float32) # 将 薪资平均值 列提取为形为(样本数, 1)的NumPy数组，并转换为float32类型。
    scaler = StandardScaler() # 创建一个标准化器实例，后续会对数据进行均值为0、方差为1的变换。
    numeric_scaled = scaler.fit_transform(numeric_features)  # 对薪资数值执行标准化：标准化后的列均值为 0，方差为 1

    # Step 2：处理学历要求、晋升路径（文本嵌入）
    df['edu_promo_text'] = df['学历要求'].fillna('') + ' ' + df['晋升路径'].fillna('') # 合并两个文本列，避免缺失值干扰
    texts = df['edu_promo_text'].tolist() # 将合并后的文本列提取为Python列表
    text_embeddings = calc_embedding(texts)  # 调用自定义的 calc_embedding 函数，对文本列表批量计算嵌入向量

    # Step 3：处理多值列表列（Multi-hot 编码）
    multi_cols = ['综合素质', '职业技能', '证书', '工作内容', '专业', '工作经验', '行业']

    for col in multi_cols: # 确保所有列均为列表类型（如果数据库返回字符串，需先转换）
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x if isinstance(x, list) else [])
            # 对每个单元格应用匿名函数：若值已经是 list 则保留原样，否则（如字符串或 None）替换为空列表 []
        else:
            df[col] = [[] for _ in range(len(df))] # 如果该列根本不存在于 DataFrame，创建一列与 DataFrame 等长的空列表列
            # 用不到


    multi_hot_parts = [] # 初始化一个空列表，用于暂存每一列的编码结果矩阵
    for col in multi_cols:
        mlb = MultiLabelBinarizer() # 实例化一个多标签二值化编码器
        encoded = mlb.fit_transform(df[col]) # fit 会扫描该列中所有出现过的标签，构建一个固定顺序的类别列表；
        # transform 将每个样本的标签列表转换为一个长度为类别总数的 0/1 向量，出现过的标签对应位置为 1，其余为 0。
        # 返回形状为 (样本数, 类别数) 的稀疏矩阵（或密集 NumPy 数组）。
        multi_hot_parts.append(encoded) # 将编码后的矩阵加入列表
        print(f"列 '{col}' 编码后维度: {encoded.shape[1]}")

    multi_hot_combined = np.hstack(multi_hot_parts)  # 沿列方向（水平）拼接列表中的所有编码矩阵，得到一个大矩阵，列数为所有列类别数之和。

    # Step 4: 融合所有特征
    X_fused = np.hstack([
        text_embeddings,  # 学历+晋升路径的语义向量
        numeric_scaled,  # 薪资平均值（标准化）
        multi_hot_combined  # 所有多值列的 multi-hot 编码
    ]) # 沿列方向（水平）拼接多个二维数组，要求所有数组的行数（样本数）相同。

    print(f"最终融合特征维度: {X_fused.shape[1]}")
    return X_fused # 返回融合后的特征矩阵，供后续监督学习模型训练使用。

#--- OLD ---#

def calc_embedding_temp(df): # Sentence-Transformer 模型，中文效果优秀的模型
    st_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
    return st_model.encode(
        df['combined_text'].tolist(),  # 将合并后的文本列转换为 Python 列表并作为输入
        convert_to_numpy=True,  # 返回 NumPy 数组而非张量
        show_progress_bar=True,  # 显示进度条
        batch_size=32  # 一次处理 32 条文本，平衡内存与速度
    )  # 调用 Sentence‑Transformer 模型的 encode 方法，将文本转换为嵌入向量