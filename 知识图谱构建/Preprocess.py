import pandas as pd
import openai
from tqdm import tqdm
import re

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
        return 'Soar'
    elif any(kwd in ct for kwd in rise_kwd):  # C轮往后
        return 'Rise'
    elif any(kwd in ct for kwd in strong_kwd): # 已上市
        return 'Strong'
    elif any(kwd in ct for kwd in other_kwd) or ct == '': # 未融资 / 不需要融资
        if size == 'E' or size == 'F' or size == 'G': # 只要规模大，就认为是稳定的
            return 'Stable'
        elif size != 'H': # 规模小
            return 'Small'
        else: # 规模未知
            return 'Unknown'
    else:
        return 'Unknown' # ct为空

def tool_addr_coding(addr):

    client = openai.OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY"  # vLLM 默认不验证 API key
    )
    # 配置本地模型 API

    prompt1 = f"""
以下是中国城市分类：

一线城市：
上海、北京、深圳、广州

新一线城市：
成都、杭州、重庆、武汉、苏州、西安、南京、长沙、郑州、天津、合肥、青岛、东莞、宁波、佛山

二线城市：
济南、无锡、沈阳、昆明、福州、厦门、温州、石家庄、大连、哈尔滨、
金华、泉州、南宁、长春、常州、南昌、南通、贵阳、嘉兴、
徐州、惠州、太原、烟台、临沂、保定、台州、绍兴、珠海、洛阳、潍坊

二线以外的城市：
乌鲁木齐、兰州、中山、盐城、海口、扬州、济宁、湖州、赣州、邯郸、南阳、唐山、芜湖、阜阳、廊坊、汕头、泰州、呼和浩特、镇江、江门、
菏泽、连云港、沧州、淄博、新乡、周口、襄阳、淮安、商丘、桂林、咸阳、上饶、银川、宿迁、漳州、遵义、滁州、绵阳、
宜昌、威海、湛江、九江、邢台、揭阳、三亚、衡阳、信阳、泰安、荆州、肇庆、蚌埠、安阳、安庆、德州、株洲、莆田、
聊城、驻马店、岳阳、亳州、柳州、宜春、宿州、黄冈、六安、常德、宁德、茂名、马鞍山、衢州

枣庄、宜宾、榆林、开封、邵阳、运城、清远、吉安、日照、许昌、包头、郴州、滨州、丽水、宣城、淮南、平顶山、东营、
南充、秦皇岛、黄石、鞍山、晋中、曲靖、孝感、抚州、宝鸡、渭南、舟山、德阳、衡水、吉林、西宁、龙岩、
焦作、十堰、濮阳、潮州、大庆、湘潭、鄂尔多斯、泸州、长治、怀化、玉林、大同、梅州、南平、黄山、
临汾、赤峰、恩施、齐齐哈尔、张家口、阳江、达州、乐山、益阳、汕尾、大理、永州、红河、北海、
河源、锦州、毕节、景德镇、晋城、凉山、韶关、三明、黔东南、眉山、承德、铜陵、荆门、黔南、
淮北、铜仁、咸宁、营口、娄底、汉中、玉溪、喀什、遂宁、拉萨、百色、天水、吕梁

忻州、盘锦、伊犁、丹东、延边、酒泉、阿克苏、梧州、牡丹江、池州、葫芦岛、佳木斯、通化、朝阳、六盘水、延安、内江、
自贡、漯河、新余、西双版纳、湘西、黔西南、张家界、昭通、丽江、贵港、嘉峪关、云浮、钦州、庆阳、
昌吉、随州、安顺、河池、萍乡、文山、通辽、辽阳、鹰潭、鹤壁、白银、呼伦贝尔、鄂州、陇南、
抚顺、普洱、广安、广元、三门峡、楚雄、贺州、绥化、阜新、本溪、铁岭、张掖、雅安、定西、
巴音郭楞、保山、德宏、松原、克拉玛依、巴中、朔州、攀枝花、安康、资阳、四平、金昌、阳泉、
商洛、平凉、防城港、甘南、白山、乌兰察布、临夏、吴忠、辽源、来宾、武威、海西、锡林郭勒、
哈密、崇左、儋州、临沧、白城、甘孜、鸡西、中卫、乌海、巴彦淖尔、和田、铜川、阿坝、兴安、
七台河、石嘴山、伊春、博尔塔拉、阿勒泰、双鸭山、黑河、林芝、鹤岗、固原、塔城、吐鲁番、海东、
大兴安岭、阿拉善、迪庆、昌都、怒江、山南、日喀则、克孜勒苏、阿里、那曲、海南、黄南、果洛、玉树、海北、三沙

你是一个城市分类大师，现在给你一个“城市-区域”格式的地址 {addr}，请无视地址中的“区域”，根据提上面给出“中国城市分类”把{addr}分为以下之一：
1. 一线：如果城市是中国的一线城市
2. 新一线：如果城市是中国的新一线城市
3. 二线：如果城市是中国的二线城市
4. 二线以外：如果城市是中国二线以外的城市
5. 外派：如果城市不是上述“中国城市分类”提到的中国的城市

注意：只输出{addr}的分类（分类必须是唯一的），不要输出思考过程，不要输出补充内容

"""

    if pd.isna(addr) or not isinstance(addr, str) or addr.strip() == "": # 空值原样返回
        return addr

    try:
        response = client.chat.completions.create(
            model="Qwen2.5-3B",
            messages=[{"role": "user", "content": prompt1}],
            temperature=0.1,
            max_tokens=64
        )
        cleaned = response.choices[0].message.content.strip()

        return cleaned

    except Exception as e:
        print(f"处理 '{addr}' 时出错: {e}")
        return addr  # 出错时保留原值

def tool_industry_coding(industry):

    client = openai.OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY"  # vLLM 默认不验证 API key
    )
    # 配置本地模型 API

    if pd.isna(industry) or not isinstance(industry, str) or industry.strip() == "":  # 空值原样返回
        return industry

    industry_list = [item.strip() for item in industry.split(',')] # 转成列表
    cleaned = [] # 空列表

    for cur_ind in industry_list:
        prompt1 = f"""
中国的行业分类国家标准如下（三大产业包含20大类，20大类包含97小类）：

# 第一产业

  1	农业
  2	林业
  3	畜牧业
  4	渔业
  5	农、林、牧、渔专业及辅助性活动

# 第二产业

  6	煤炭开采和洗选业
  7	石油和天然气开采业
  8	黑色金属矿采选业
  9	有色金属矿采选业
  10	非金属矿采选业
  11	开采专业及辅助性活动
  12	其他采矿业

  13	农副食品加工业
  14	食品制造业
  15	酒、饮料和精制茶制造业
  16	烟草制品业
  17	纺织业
  18	纺织服装、服饰业
  19	皮革、毛皮、羽毛及其制品和制鞋业
  20	木材加工和木、竹、藤、棕、草制品业
  21	家具制造业
  22	造纸和纸制品业
  23	印刷和记录媒介复制业
  24	文教、工美、体育和娱乐用品制造业
  25	石油、煤炭及其他燃料加工业
  26	化学原料和化学制品制造业
  27	医药制造业
  28	化学纤维制造业
  29	橡胶和塑料制品业
  30	非金属矿物制品业
  31	黑色金属冶炼和压延加工业
  32	有色金属冶炼和压延加工业
  33	金属制品业
  34	通用设备制造业
  35	专用设备制造业
  36	汽车制造业
  37	铁路、船舶、航空航天和其他运输设备制造业
  38	电气机械和器材制造业
  39	计算机、通信和其他电子设备制造业
  40	仪器仪表制造业
  41	其他制造业
  42	废弃资源综合利用业
  43	金属制品、机械和设备修理业

  44	电力、热力生产和供应业
  45	燃气生产和供应业
  46	水的生产和供应业

  47	房屋建筑业
  48	土木工程建筑业
  49	建筑安装业
  50	建筑装饰、装修和其他建筑业

# 第三产业

  51	批发业
  52	零售业

  53	铁路运输业
  54	道路运输业
  55	水上运输业
  56	航空运输业
  57	管道运输业
  58	多式联运和运输代理业
  59	装卸搬运和仓储业
  60	邮政业

  61	住宿业
  62	餐饮业

  63	电信、广播电视和卫星传输服务
  64	互联网和相关服务
  65	软件和信息技术服务业

  66	货币金融服务
  67	资本市场服务
  68	保险业
  69	其他金融业

  70	房地产业

  71	租赁业
  72	商务服务业

  73	研究和试验发展
  74	专业技术服务业
  75	科技推广和应用服务业

  76	水利管理业
  77	生态保护和环境治理业
  78	公共设施管理业
  79	土地管理业

  80	居民服务业
  81	机动车、电子产品和日用产品修理业
  82	其他服务业

  83	教育

  84	卫生
  85	社会工作

  86	新闻和出版业
  87	广播、电视、电影和录音制作业
  88	文化艺术业
  89	体育
  90	娱乐业

  91	中国共产党机关
  92	国家机构
  93	人民政协、民主党派
  94	社会保障
  95	群众团体、社会团体和其他成员组织
  96	基层群众自治组织及其他组织

  97	国际组织

你是一个就业领域的专家，请思考并判断{cur_ind}属于上述标准的哪一个小类，并输出“小类的编号”。
注意：
1. 不要输出思考过程，也不要输出任何解释内容！！！
2. 只输出一个编号，如果你认为“{cur_ind}”有多个适合的小类，则输出你认为最匹配的那个。

"""

        try:
            response = client.chat.completions.create(
                model="Qwen2.5-3B",
                messages=[{"role": "user", "content": prompt1}],
                temperature=0.1,
                max_tokens=64
            )
            result = response.choices[0].message.content.strip()
            if 98 > int(result) or int(result) < 0:
                cleaned.append(response.choices[0].message.content.strip())

        except Exception as e:
            print(f"处理 '{cur_ind}' 时出错: {e}")
            return []  # 出错时返回空值
    return cleaned


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

#-------------------------#

def preprocess_size(loc_df): # 将公司规模列替换为字母代码
    if '公司规模' in loc_df.columns:
        loc_df['公司规模'] = loc_df['公司规模'].apply(tool_size_coding)
    else:
        print("Error")
    return loc_df

def preprocess_develop(loc_df):
    if '公司类型' in loc_df.columns:
        loc_df['公司类型'] = loc_df.apply(
            lambda row: tool_development_coding(row['公司类型'], row['公司规模']),
            axis=1
        )
    else:
        print("Error")
    return loc_df

def preprocess_city_type(loc_df):
    if "地址" in loc_df.columns: # 确保所查列存在
        loc_df["城市类型"] = loc_df["地址"].copy() # 新建一个列来存城市类型
        tqdm.pandas(desc="清洗地址") # 使用 tqdm 显示进度
        loc_df["城市类型"] = loc_df["城市类型"].progress_apply(tool_addr_coding)
    else:
        print("Error")
    return loc_df

def preprocess_industry(loc_df):
    if "所属行业" in loc_df.columns: # 确保所查列存在
        tqdm.pandas(desc="清洗所属行业") # 使用 tqdm 显示进度
        loc_df["所属行业"] = loc_df["所属行业"].progress_apply(tool_industry_coding)
    else:
        print("Error")
    return loc_df

def preprocess_salary(cur_df):
    if '薪资范围' not in cur_df.columns:
        print("错误：未找到‘薪资范围’列")
        return

    cur_df['薪资范围_原始'] = cur_df['薪资范围'].copy()
    tqdm.pandas(desc="清洗薪资")
    cur_df['薪资范围'] = cur_df['薪资范围'].progress_apply(tool_salary_coding)

    return cur_df

if __name__ == '__main__':
    # 读入excel
    input_file = 'partial.xlsx'
    df = pd.read_excel(input_file)
    # 预处理
    df_after = preprocess_size(df)
    df_after = preprocess_develop(df_after)
    df_after = preprocess_city_type(df_after)
    df_after = preprocess_industry(df_after)
    df_after = preprocess_salary(df_after)
    # 写入excal
    output_file = 'partial_processed.xlsx'
    df.to_excel(output_file,index=False)
    print(f'处理完成，结果已保存至 {output_file}')

