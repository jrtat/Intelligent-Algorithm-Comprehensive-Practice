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

def init_data_nli_raw(df):
    def extract_row(row):
        """
        把df中的一行转成一个字符串
        """
        industry = row['行业']
        salary = row['薪资范围']
        description = row['详情']
        text = f'''
    该岗位薪资为{salary}每月。该岗位的详细职责和要求（包含了该岗位对技术能力的要求）如下：{description}，属于“{industry}”行业
    '''
        return text
    df['text_for_llm'] = df.apply(extract_row, axis=1)
    return df['text_for_llm'].tolist()