import pandas as pd
import re
import math
import os

# 1. 定义：薪资范围 -> 平均月薪 的解析函数
def parse_to_avg_monthly_salary(salary_str):
    if pd.isna(salary_str) or str(salary_str).strip() in ['面议', '未知']:
        return None
    
    s = str(salary_str).strip().lower()
    
    # 提取字符串中的所有数字（支持小数，如 1.5, 120）
    nums = re.findall(r'\d+\.?\d*', s)
    if not nums:
        return None
        
    # 获取区间的最低和最高值
    if len(nums) >= 2:
        try:
            low, high = float(nums[0]), float(nums[1])
        except ValueError:
            return None
    else:
        try:
            low = high = float(nums[0])
        except ValueError:
            return None
        
    # 判断量级单位
    multiplier = 1
    if '万' in s:
        multiplier = 10000
    elif '千' in s or 'k' in s:
        multiplier = 1000
        
    # 判断时间单位并转换为“月薪” (默认月薪)
    # 假设每个月平均计薪工作日为 21.75 天
    period_multiplier = 1
    if '天' in s or 'day' in s:
        period_multiplier = 21.75
    elif '年' in s or 'year' in s:
        period_multiplier = 1 / 12.0
        
    # 计算平均值：(低+高)/2 * 量级单位 * 时间单位转换
    avg_salary = (low + high) / 2 * multiplier * period_multiplier
    
    return round(avg_salary)

# 2. 定义：公司规模 -> 统一类别 的解析函数
def categorize_company_size(size_str):
    if pd.isna(size_str):
        return '未知'
    
    s = str(size_str).strip()
    
    # 根据题意直接基于特征字判断
    if '以下' in s:
        return '小'
    if '以上' in s:
        return '很大'
        
    # 如果是区间（如 300-499人），提取最大数字判断位数
    nums = re.findall(r'\d+', s)
    if nums:
        max_num = max([int(n) for n in nums])
        if max_num < 100:
            return '很小'
        elif max_num < 500:
            return '小'
        elif max_num < 1000:
            return '中'
        else:               
            return '大'
            
    return '未知'

# 3. 定义：平均月薪 -> 岗位级别 的判定函数
def get_job_level(salary):
    if pd.isna(salary):
        return '未知'
    if salary < 9000:
        return '低级'
    elif salary <= 18000:
        return '中级'
    else:
        return '高级'

# ==================== 主执行流程 ====================
def main():
    print(f"📁 当前工作目录: {os.getcwd()}")
    target_file = 'initdata.xls'
    
    if not os.path.exists(target_file):
        print(f"❌ 错误：未在目录中找到 {target_file}。")
        print(f"当前目录下的文件有: {os.listdir('.')}")
        return

    print(f"🚀 开始读取 {target_file} 数据...")
    try:
        # 特别注意：Windows 下如果 Excel 打开了该文件，会报错 PermissionError
        # 指定 engine='xlrd' 以确保使用正确的引擎读取 .xls
        df = pd.read_excel(target_file, engine='xlrd') 
        print(f"✅ 读取成功！共 {len(df)} 行数据。")
    except PermissionError:
        print(f"❌ 权限错误：请先关闭正在运行的 Excel 窗口（{target_file}），然后再试。")
        return
    except Exception as e:
        print(f"❌ 读取 Excel 时发生未知错误: {e}")
        return

    # 规则 1: 转换并替换薪资列
    print("⏳ 正在处理【薪资范围】...")
    if '薪资范围' in df.columns:
        df['平均月薪'] = df['薪资范围'].apply(parse_to_avg_monthly_salary)
        # df.drop(columns=['薪资范围'], inplace=True, errors='ignore') # 暂时保留对比
    else:
        print(f"⚠️ 找不到【薪资范围】列，当前列名有: {df.columns.tolist()}")

    # 规则 2: 规范化公司规模
    print("⏳ 正在处理【公司规模】...")
    if '公司规模' in df.columns:
        df['公司规模'] = df['公司规模'].apply(categorize_company_size)

    # 规则 3: 删除任务要求的冗余列
    print("⏳ 正在剔除冗余字段...")
    cols_to_drop = ['岗位编码', '更新日期', '岗位来源地址']
    df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

    # 规则 4: 基于清洗后的“平均月薪”生成“岗位级别”
    print("⏳ 正在生成【岗位级别】标签...")
    if '平均月薪' in df.columns:
        df['岗位级别'] = df['平均月薪'].apply(get_job_level)

    # 导出文件
    output_file = 'clean_1.xls'
    xlsx_backup = 'clean_1.xlsx'
    
    print(f"💾 正在导出结果...")
    try:
        # xlwt 只能处理 65535 行以下的数据
        if len(df) > 60000:
            raise ValueError("数据量较大，建议使用 .xlsx 格式")
            
        df.to_excel(output_file, index=False, engine='xlwt')
        print(f"✅ 数据清洗完成！已保存至 {output_file}")
    except Exception as e:
        print(f"⚠️ 无法保存为 .xls (原因: {e})，尝试保存为 {xlsx_backup}...")
        try:
            df.to_excel(xlsx_backup, index=False, engine='openpyxl')
            print(f"✅ 成功保存至 {xlsx_backup}！")
        except Exception as e2:
            print(f"❌ 最终导出也失败了: {e2}")

if __name__ == "__main__":
    main()