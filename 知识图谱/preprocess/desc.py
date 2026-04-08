import pandas as pd

def preprocess_job_desc(loc_df):
  # print(df["岗位详情"].head())
  loc_df["岗位详情"] = loc_df["岗位详情"].replace("<br>", "")
  loc_df["岗位详情"] = loc_df["岗位详情"].replace(r"<[^>]+>", "", regex=True)  # 移除所有HTML标签
  return 

def preprocess_company_desc(loc_df):
  # print(df["公司详情"].head())
  loc_df["公司详情"] = loc_df["公司详情"].replace("<br>", "")
  loc_df["公司详情"] = loc_df["公司详情"].replace(r"<[^>]+>", "", regex=True)  # 移除所有HTML标签
  return 
