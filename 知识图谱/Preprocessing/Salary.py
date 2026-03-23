import pandas as pd
from tqdm import tqdm
import re

def tool_salary_coding(text):  # 清洗单条薪资文本，返回标准化的"最低月薪-最高月薪"格式字符串

    if pd.isna(text) or not isinstance(text, str):
        return text
    text = text.strip()
    if text == "" or "面议" in text:
        return "面议"

    pattern = r'([\d\.]+)\s*-\s*([\d\.]+)|([\d\.]+)'  # 提取数字范围（两个数字或单个数字）
    match = re.search(pattern, text)
    # 提取：1. 单个数字； 2. “数字-数字”格式；

    if not match:
        return text  # 无法解析，保留原样

    if match.group(1) and match.group(2):  # 提取出上下界
        tmp_str1, tmp_str2 = match.group(1), match.group(2)
        low, high = float(tmp_str1), float(tmp_str2)

    else:
        tmp_str = match.group(3)
        low = high = float(tmp_str)

    unit_part = re.sub(pattern, '', text, count=1).strip()

    # 获取剩余字符串（单位、后缀等）

    print(unit_part)

    if '万' in unit_part:  # 判断是否包含“万”并先转换为元
        low *= 10000
        high *= 10000
        # 移除已处理的“万”以避免后续误判
        unit_part = unit_part.replace('万', '').strip()

    is_daily = False  # 判断是否为日薪（单位包含“元/天”、“日”或数值明显小）
    if any(k in unit_part for k in ['元/天', '/天', '日']):
        is_daily = True
    elif low < 2000 and high < 2000:
        is_daily = True  # 没有明确单位但数值很小，视为日薪

    if is_daily:
        low = low * 24
        high = high * 24
        unit_part = re.sub(r'元?/天|日', '', unit_part)  # 移除日薪标记

    is_yearly = False  # 判断是否为年薪（单位包含“元/年”、“年”或数值明显大）
    if any(k in unit_part for k in ['元/年', '/年', '年']):
        is_yearly = True
    elif low > 48000 or high > 48000:
        is_yearly = True  # 没有明确单位但数值很大，视为年薪

    if is_yearly:
        low = low / 12
        high = high / 12
        unit_part = re.sub(r'元?/年|年', '', unit_part)  # 移除年薪标记

    xin_match = re.search(r'[•·*](\d+)薪', unit_part)  # 处理“·X薪”后缀（如“·13薪”）
    if xin_match:
        xin = float(xin_match.group(1))
        # 乘以 xin/12，即 xin薪折算成12个月的平均月薪
        low = low * xin / 12
        high = high * xin / 12
        print("薪")
        unit_part = unit_part.replace(xin_match.group(0), '')  # 移除“·X薪”后缀

    low = int(low)
    high = int(high)  # 最终取整（截断小数部分）

    return f"{low}-{high}"

def preprocess_salary(loc_df):
    if '薪资范围' not in loc_df.columns:
        print("错误：未找到‘薪资范围’列")
        return loc_df

    tqdm.pandas(desc="清洗薪资")
    loc_df['薪资范围'] = loc_df['薪资范围'].progress_apply(tool_salary_coding)
    return loc_df
