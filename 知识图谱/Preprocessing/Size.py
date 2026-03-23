import pandas as pd

def tool_size_coding(size):
    if pd.isna(size) or size == '': # 空白的情况
        return 'H'
    size = str(size).strip()
    if '20人以下' in size:
        return 'A'
    if '20-99人' in size:
        return 'B'
    if '100-299人' in size:
        return 'C'
    if '300-499人' in size:
        return 'D'
    if '500-999人' in size:
        return 'E'
    if '1000-9999人' in size:
        return 'F'
    if '10000人以上' in size:
        return 'G'
    return 'H' # 异常内容的情况
    # 防止前后空格导致识别不出来

def preprocess_size(loc_df): # 将公司规模列替换为字母代码
    if '公司规模' in loc_df.columns:
        loc_df['公司规模'] = loc_df['公司规模'].apply(tool_size_coding)
    else:
        print("Error")
    return loc_df