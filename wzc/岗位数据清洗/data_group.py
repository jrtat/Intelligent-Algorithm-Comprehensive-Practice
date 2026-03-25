import pandas as pd
import re
import os

def clean_and_group():
    input_path = 'data/clean_job.xlsx'
    output_path = 'data/clean_job_group.xlsx'
    
    if not os.path.exists(input_path):
        print(f"找不到输入文件: {input_path}")
        return
        
    print(f"正在读取文件: {input_path}")
    df = pd.read_excel(input_path)
    print(f"原始数据总行数: {len(df)}")
    
    # ==== 聚合逻辑定义 ====
    
    def process_industry(series):
        """所属行业：用'/'或','分隔，去重，'|'拼接"""
        industries = set()
        for item in series.dropna():
            # 正则匹配不同类型的分隔符
            parts = re.split(r'[/,]', str(item))
            for p in parts:
                p = p.strip()
                if p:
                    industries.add(p)
        return '|'.join(sorted(list(industries)))
    
    def process_company(series):
        """公司详情：直接融合，'|'分隔"""
        comps = [str(x).strip() for x in series.dropna() if str(x).strip()]
        return '|'.join(comps)
        
    def process_job_detail(series):
        """岗位详情：直接融合，'&'分隔"""
        details = [str(x).strip() for x in series.dropna() if str(x).strip()]
        return '&'.join(details)
        
    def process_level(series):
        """岗位级别（枚举值）：去重，'|'分隔"""
        levels = set()
        for x in series.dropna():
            x_str = str(x).strip()
            if x_str:
                levels.add(x_str)
        return '|'.join(sorted(list(levels)))

    print("正在按「岗位名称」分组处理...")
    
    # 确保列名存在以防报错
    expected_columns = ['岗位名称', '所属行业', '岗位详情', '公司详情', '岗位级别']
    missing = [c for c in expected_columns if c not in df.columns]
    if missing:
        print(f"警告：输入文件缺少以下列：{missing}")
        
    # 执行 groupby 和自定义聚合
    grouped_df = df.groupby('岗位名称', as_index=False).agg({
        '所属行业': process_industry,
        '公司详情': process_company,
        '岗位详情': process_job_detail,
        '岗位级别': process_level
    })
    
    print(f"处理完成，唯一的岗位种类数: {len(grouped_df)}")
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"正在保存结果至: {output_path}")
    grouped_df.to_excel(output_path, index=False)
    print("保存成功！")
    
    return grouped_df

if __name__ == "__main__":
    df_grouped = clean_and_group()
    
    # TODO: 下一步将利用 LLM API 进行标注
    # 可以遍历 df_grouped 后构造 Prompt 发送给 LLM
    # 例如：
    # for index, row in df_grouped.iterrows():
    #     prompt = f"岗位名称: {row['岗位名称']}\n所属行业: {row['所属行业']}..."
    #     ...调用 LLM 模型...
