import pandas as pd
from Preprocessing.Salary import preprocess_salary
from Preprocessing.Size import preprocess_size
from Preprocessing.Development import preprocess_development
from Preprocessing.Industry import preprocess_industry
from Preprocessing.City_Type import preprocess_city_type
from Preprocessing.Degree import preprocess_degree
from Preprocessing.Create import preprocess_create
from Preprocessing.Stress import preprocess_stress
from Preprocessing.Communicate import preprocess_communicate

if __name__ == '__main__':

    # 读入excel
    input_file = 'partial.xlsx' # 改成正确的名字
    df = pd.read_excel(input_file)

    # 调用各个清洗函数
    df_after = preprocess_size(df)
    df_after = preprocess_development(df_after)
    df_after = preprocess_city_type(df_after)
    df_after = preprocess_industry(df_after)
    df_after = preprocess_salary(df_after)
    df_after = preprocess_degree(df_after)
    df_after = preprocess_create(df_after)
    df_after = preprocess_stress(df_after)
    df_after = preprocess_communicate(df_after)

    # 写入excal
    output_file = 'partial_processed.xlsx' # 改成正确的名字
    df.to_excel(output_file,index=False)
    print(f'处理完成，结果已保存至 {output_file}')

