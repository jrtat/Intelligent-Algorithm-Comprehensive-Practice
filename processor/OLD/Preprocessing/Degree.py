import openai
from tqdm import tqdm

def tool_degree_coding(text):

    client = openai.OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY"
    )

    # 构造prompt
    prompt = f"""
你是一个信息提取助手。现在有如下岗位详情：
{text}

请从以下岗位详情文本中提取两个信息：
1. 学历要求：如果岗位详情中明确提到了对学历的要求，请输出具体级别:
    中专及以上：如果岗位详情中有“中专”，“中专学历”，或者含义类似的词
    大专及以上：如果岗位详情中有“大专”，“大专学历”，“专科”，“专科学历”，或者含义类似的词
    本科及以上：如果岗位详情中有“本科”，“本科学历”，或者含义类似的词
    硕士及以上：如果岗位详情中有“硕士”，“硕士学历”，“硕士研究生”，“硕士毕业生”，或者含义类似的词
    博士及以上：如果岗位详情中有“博士”，“博士学历”，“博士研究生”，“博士毕业生”，或者含义类似的词
    无任何要求：如果岗位详情中没有与学历要求相关的内容
2. 学校要求：如果文中提到了对毕业院校的要求，请输出具体级别:
    双一流优先：如果岗位详情中有“双一流学校毕业生优先”，“双一流学科毕业生优先”，或者含义类似的词
    985/211优先：如果岗位详情中有“985毕业生优先”，“211毕业生优先”，或者含义类似的词
    无任何要求：如果岗位详情中没有与学校要求相关的内容

请按以下格式输出，用逗号分隔两个部分：
学历要求: xxx, 学校要求: xxx

注意：只输出“学历要求: xxx, 学校要求: xxx”，不要输出思考过程，不要输出解释文本

"""
    try:
        response = client.chat.completions.create(
            model="Qwen2.5-3B",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100,
        )
        result = response.choices[0].message.content.strip()
        # 解析结果
        parts = result.split(',')
        degree = "无任何要求"
        school = "无任何要求"
        for p in parts:
            if p.startswith("学历要求："):
                degree = p.replace("学历要求：", "").strip()
            elif p.startswith("学校要求："):
                school = p.replace("学校要求：", "").strip()
        return [degree, school]
    except Exception as e:
        print(f"调用模型出错: {e}")
        return ["无任何要求", "无任何要求"]

def preprocess_degree(loc_df):
    if '岗位详情' not in loc_df.columns:
        print("错误：未找到‘岗位详情’列")
        return loc_df

    tqdm.pandas(desc="岗位详情")
    loc_df['学历要求'] = loc_df['岗位详情'].progress_apply(tool_degree_coding)

    return loc_df
