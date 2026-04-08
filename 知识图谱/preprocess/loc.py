import pandas as pd

def preprocess_loc(loc_df):
    loc_df['地址'] = loc_df['地址'].str.split('-').str[0]
    return loc_df