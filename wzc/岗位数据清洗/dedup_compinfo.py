import pandas as pd
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', 'job_tollm.xlsx')
    
    if not os.path.exists(file_path):
        print(f"Error: 找不到文件 {file_path}")
        return
        
    print(f"正在读取文件: {file_path}")
    df = pd.read_excel(file_path)
    
    if '公司特质' not in df.columns:
        print(f"Error: 文件中不存在「公司特质」列。实际列为: {list(df.columns)}")
        # 兼容一下，如果还是旧的「行业特质」，那也能处理
        if '行业特质' in df.columns:
            target_col = '行业特质'
            print(f"找到备用列「{target_col}」进行处理")
        else:
            return
    else:
        target_col = '公司特质'
        
    def dedup_traits(traits_str):
        if pd.isna(traits_str) or not str(traits_str).strip():
            return ""
        
        # 1. 按 '|' 首尾去空格并按字符分割
        parts = str(traits_str).split('|')
        
        # 2. 清理每个段落的前后空白并去除空字符串
        clean_parts = [p.strip() for p in parts if p.strip()]
        
        # 3. 有序去重
        seen = set()
        deduped = []
        for p in clean_parts:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
                
        # 4. 重新使用 '|' 连接
        return '|'.join(deduped)
        
    print(f"开始对「{target_col}」进行按 '|' 切分并去重...")
    df[target_col] = df[target_col].apply(dedup_traits)
    
    # 直接覆盖源文件
    print(f"正在覆盖保存至: {file_path}")
    df.to_excel(file_path, index=False)
    print("去重并覆盖保存成功！")
    
if __name__ == "__main__":
    main()
