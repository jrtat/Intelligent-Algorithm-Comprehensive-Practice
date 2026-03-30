import pandas as pd
import openai
from tqdm import tqdm


INDUSTRY_MAP = {} # 构建从编号到（产业，大类字母，大类名称，小类名称）的映射

# 第一产业 (A类)
FIRST_INDUSTRY = "第一产业"

A_CLASS = ("A", "农、林、牧、渔业")
FIRST_SUB = [
    (1, "农业"), (2, "林业"), (3, "畜牧业"), (4, "渔业"),
    (5, "农、林、牧、渔专业及辅助性活动")
]
for code, name in FIRST_SUB:
    INDUSTRY_MAP[code] = (FIRST_INDUSTRY, A_CLASS[0], A_CLASS[1], name)

# 第二产业 (B, C, D, E类)
SECOND_INDUSTRY = "第二产业"

B_CLASS = ("B", "采矿业")
B_SUB = [
    (6, "煤炭开采和洗选业"), (7, "石油和天然气开采业"),
    (8, "黑色金属矿采选业"), (9, "有色金属矿采选业"),
    (10, "非金属矿采选业"), (11, "开采专业及辅助性活动"),
    (12, "其他采矿业")
]
for code, name in B_SUB:
    INDUSTRY_MAP[code] = (SECOND_INDUSTRY, B_CLASS[0], B_CLASS[1], name)

C_CLASS = ("C", "制造业")
C_SUB = [
    (13, "农副食品加工业"), (14, "食品制造业"), (15, "酒、饮料和精制茶制造业"),
    (16, "烟草制品业"), (17, "纺织业"), (18, "纺织服装、服饰业"),
    (19, "皮革、毛皮、羽毛及其制品和制鞋业"), (20, "木材加工和木、竹、藤、棕、草制品业"),
    (21, "家具制造业"), (22, "造纸和纸制品业"), (23, "印刷和记录媒介复制业"),
    (24, "文教、工美、体育和娱乐用品制造业"), (25, "石油、煤炭及其他燃料加工业"),
    (26, "化学原料和化学制品制造业"), (27, "医药制造业"), (28, "化学纤维制造业"),
    (29, "橡胶和塑料制品业"), (30, "非金属矿物制品业"), (31, "黑色金属冶炼和压延加工业"),
    (32, "有色金属冶炼和压延加工业"), (33, "金属制品业"), (34, "通用设备制造业"),
    (35, "专用设备制造业"), (36, "汽车制造业"), (37, "铁路、船舶、航空航天和其他运输设备制造业"),
    (38, "电气机械和器材制造业"), (39, "计算机、通信和其他电子设备制造业"),
    (40, "仪器仪表制造业"), (41, "其他制造业"), (42, "废弃资源综合利用业"),
    (43, "金属制品、机械和设备修理业")
]
for code, name in C_SUB:
    INDUSTRY_MAP[code] = (SECOND_INDUSTRY, C_CLASS[0], C_CLASS[1], name)

D_CLASS = ("D", "电力、热力、燃气及水生产和供应业")
D_SUB = [
    (44, "电力、热力生产和供应业"), (45, "燃气生产和供应业"),
    (46, "水的生产和供应业")
]
for code, name in D_SUB:
    INDUSTRY_MAP[code] = (SECOND_INDUSTRY, D_CLASS[0], D_CLASS[1], name)

E_CLASS = ("E", "建筑业")
E_SUB = [
    (47, "房屋建筑业"), (48, "土木工程建筑业"),
    (49, "建筑安装业"), (50, "建筑装饰、装修和其他建筑业")
]
for code, name in E_SUB:
    INDUSTRY_MAP[code] = (SECOND_INDUSTRY, E_CLASS[0], E_CLASS[1], name)

# 第三产业 (F类到T类)
THIRD_INDUSTRY = "第三产业"

F_CLASS = ("F", "批发和零售业")
F_SUB = [(51, "批发业"), (52, "零售业")]
for code, name in F_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, F_CLASS[0], F_CLASS[1], name)

G_CLASS = ("G", "交通运输、仓储和邮政业")
G_SUB = [
    (53, "铁路运输业"), (54, "道路运输业"), (55, "水上运输业"),
    (56, "航空运输业"), (57, "管道运输业"), (58, "多式联运和运输代理业"),
    (59, "装卸搬运和仓储业"), (60, "邮政业")
]
for code, name in G_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, G_CLASS[0], G_CLASS[1], name)

H_CLASS = ("H", "住宿和餐饮业")
H_SUB = [(61, "住宿业"), (62, "餐饮业")]
for code, name in H_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, H_CLASS[0], H_CLASS[1], name)

I_CLASS = ("I", "信息传输、软件和信息技术服务业")
I_SUB = [
    (63, "电信、广播电视和卫星传输服务"),
    (64, "互联网和相关服务"),
    (65, "软件和信息技术服务业")
]
for code, name in I_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, I_CLASS[0], I_CLASS[1], name)

J_CLASS = ("J", "金融业")
J_SUB = [
    (66, "货币金融服务"), (67, "资本市场服务"),
    (68, "保险业"), (69, "其他金融业")
]
for code, name in J_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, J_CLASS[0], J_CLASS[1], name)

K_CLASS = ("K", "房地产业")
K_SUB = [(70, "房地产业")]
for code, name in K_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, K_CLASS[0], K_CLASS[1], name)

L_CLASS = ("L", "租赁和商务服务业")
L_SUB = [(71, "租赁业"), (72, "商务服务业")]
for code, name in L_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, L_CLASS[0], L_CLASS[1], name)

M_CLASS = ("M", "科学研究和技术服务业")
M_SUB = [
    (73, "研究和试验发展"), (74, "专业技术服务业"),
    (75, "科技推广和应用服务业")
]
for code, name in M_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, M_CLASS[0], M_CLASS[1], name)

N_CLASS = ("N", "水利、环境和公共设施管理业")
N_SUB = [
    (76, "水利管理业"), (77, "生态保护和环境治理业"),
    (78, "公共设施管理业"), (79, "土地管理业")
]
for code, name in N_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, N_CLASS[0], N_CLASS[1], name)

O_CLASS = ("O", "居民服务、修理和其他服务业")
O_SUB = [
    (80, "居民服务业"), (81, "机动车、电子产品和日用产品修理业"),
    (82, "其他服务业")
]
for code, name in O_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, O_CLASS[0], O_CLASS[1], name)

P_CLASS = ("P", "教育")
P_SUB = [(83, "教育")]
for code, name in P_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, P_CLASS[0], P_CLASS[1], name)

Q_CLASS = ("Q", "卫生和社会工作")
Q_SUB = [(84, "卫生"), (85, "社会工作")]
for code, name in Q_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, Q_CLASS[0], Q_CLASS[1], name)

R_CLASS = ("R", "文化、体育和娱乐业")
R_SUB = [
    (86, "新闻和出版业"), (87, "广播、电视、电影和录音制作业"),
    (88, "文化艺术业"), (89, "体育"), (90, "娱乐业")
]
for code, name in R_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, R_CLASS[0], R_CLASS[1], name)

S_CLASS = ("S", "公共管理、社会保障和社会组织")
S_SUB = [
    (91, "中国共产党机关"), (92, "国家机构"), (93, "人民政协、民主党派"),
    (94, "社会保障"), (95, "群众团体、社会团体和其他成员组织"),
    (96, "基层群众自治组织及其他组织")
]
for code, name in S_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, S_CLASS[0], S_CLASS[1], name)

T_CLASS = ("T", "国际组织")
T_SUB = [(97, "国际组织")]
for code, name in T_SUB:
    INDUSTRY_MAP[code] = (THIRD_INDUSTRY, T_CLASS[0], T_CLASS[1], name)

def format_industry_codes(code_list): # 把编号再转回文本
    if not code_list:
        return "未知"

    formatted = []
    for code_str in code_list:
        try:
            code = int(code_str)  # 转为整数，避免前导零问题
            if code not in INDUSTRY_MAP:
                raise KeyError
            industry, letter, big_name, small_name = INDUSTRY_MAP[code]

            # 产业中文转换
            if industry == "第一产业":
                industry_cn = "一"
            elif industry == "第二产业":
                industry_cn = "二"
            else:
                industry_cn = "三"

            # 构建输出
            formatted_str = f"第{industry_cn}产业；{letter}类：{big_name}；{code} {small_name}"
            formatted.append(formatted_str)

        except (ValueError, KeyError): # 无效编号，用“未知”占位
            formatted.append("未知")

    # 多个行业用分号分隔
    return "/".join(formatted) if formatted else "未知"

def tool_industry_coding(industry , desc):

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

  6	    煤炭开采和洗选业
  7	    石油和天然气开采业
  8	    黑色金属矿采选业
  9     有色金属矿采选业
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

你是一个就业领域的专家，现在有一个岗位描述如下：
{desc}

又有岗位信息称该岗位属于：{cur_ind} 行业

请结合岗位描述思考并判断该岗位属于中国的行业分类国家标准的哪一个小类，并输出“小类的编号”。

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

def preprocess_industry(loc_df):
    if '所属行业' not in loc_df.columns:
        print("错误：未找到‘所属行业’列")
        return loc_df

    tqdm.pandas(desc="清洗所属行业")
    # 先得到编号列表
    loc_df["所属行业"] = loc_df.progress_apply(
        lambda row: tool_industry_coding(row['所属行业'], row['岗位详情']),
        axis=1
    )
    # 再格式化为所需字符串
    loc_df["所属行业（标准）"] = loc_df["所属行业（标准）"].apply(format_industry_codes)
    return loc_df
