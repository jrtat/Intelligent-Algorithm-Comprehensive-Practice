import pandas as pd

def tool_development_coding(company_type, size):

    if pd.isna(company_type) or not isinstance(company_type, str): # 处理空值或非字符串
        ct = ''
    else:
        ct = company_type.lower()

    soar_kwd = ['天使轮', 'a轮', 'b轮']                     # 初创期
    rise_kwd = ['c轮', 'd轮', 'e轮', 'f轮', 'g轮']          # 上升期
    strong_kwd = ['已上市']                                     # 已上市
    other_kwd = ['未融资', '不需要融资']           # 未融资等状态

    if any(kwd in ct for kwd in soar_kwd):  # 天使轮/A/B轮
        return '公司处于天使轮/A轮/B轮，正位于高速上升期'
    elif any(kwd in ct for kwd in rise_kwd):  # C轮往后
        return '公司处于C轮/D轮/E轮/F轮，正位于平稳上升期'
    elif any(kwd in ct for kwd in strong_kwd): # 已上市
        return '公司已上市，市场认可度高'
    elif any(kwd in ct for kwd in other_kwd) or ct == '': # 未融资 / 不需要融资
        if size == 'E' or size == 'F' or size == 'G': # 只要规模大，就认为是稳定的
            return '公司未融资或不需要融资，且公司规模较大，比较稳定'
        elif size != 'H': # 规模小
            return '公司未融资或不需要融资，且公司规模较小，稳定性尚可'
        else: # 规模未知
            return '公司未融资或不需要融资，公司规模未知，发展情况未知'
    else:
        return '公司类型未知，发展情况未知' # ct为空

def preprocess_development(loc_df):
    if '公司类型' not in loc_df.columns:
        print("错误：未找到‘公司类型’列")
        return loc_df
    loc_df["公司发展情况"] = loc_df["公司类型"].copy() # 新建一个列来存城市类型
    loc_df['公司发展情况'] = loc_df.apply(
        lambda row: tool_development_coding(row['公司类型'], row['公司规模（离散）']),
        axis=1
    )
    return loc_df
