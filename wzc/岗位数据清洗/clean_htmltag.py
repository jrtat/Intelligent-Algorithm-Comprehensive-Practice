import pandas as pd
import re
import os
import html

# 修正文件读取路径：根据目录结构，数据在 data/ 子目录下
input_file = os.path.join('data', 'clean_jobAndComp.xlsx')
output_file = os.path.join('data', 'clean_job_final.xlsx')

if not os.path.exists(input_file):
    # 兼容性处理：尝试另一个常用的输入文件名
    input_file = os.path.join('data', 'clean_job.xlsx')

print(f"🚀 正在从 {input_file} 读取数据...")
df = pd.read_excel(input_file)

# 清洗函数：增强版，去掉 HTML 标签并处理实体符号（如 &nbsp;）
def clean_html_content(text):
    if pd.isna(text):
        return ""
    # 1. 解码 HTML 实体 (例如 &amp; -> &)
    cleaned = html.unescape(str(text))
    # 2. 去掉所有 <...> 标签
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    # 3. 处理特殊的空白字符和换行
    cleaned = re.sub(r'[\r\n\t]+', ' ', cleaned)
    # 4. 去掉多余空格
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

print("⏳ 正在清洗【岗位详情】和【公司详情】...")
df['岗位详情'] = df['岗位详情'].apply(clean_html_content)
if '公司详情' in df.columns:
    df['公司详情'] = df['公司详情'].apply(clean_html_content)

# 去重处理（基于任务要求的“静态保存”，确保数据唯一性）
initial_len = len(df)
# 尝试基于核心列去重，如果列不存在则跳过
subset_cols = [c for c in ['岗位名称', '公司名称', '地址'] if c in df.columns]
if subset_cols:
    df.drop_duplicates(subset=subset_cols, inplace=True)
print(f"🧹 去重完成：从 {initial_len} 行剩至 {len(df)} 行")

# 最终导出保存
df.to_excel(output_file, index=False)
print(f"✅ 处理完成！最终文件已保存到: {output_file}")

# 打印示例展示效果
print("\n--- 清洗后的岗位详情示例 ---")
print(df['岗位详情'].iloc[0][:150] + "...")
