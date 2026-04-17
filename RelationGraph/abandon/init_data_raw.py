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