import openai
from tqdm import tqdm

def tool_ability_coding(text):

    client = openai.OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY"
    )

    # 构造prompt
    prompt = f"""
你是一个专业的信息提取助手。现在有如下岗位详情：
{text}

请从中提取出该岗位对应聘人的能力需求，主要涉及专业技能方面，不涉及以下方面：
1. 不要涉及创新能力，沟通能力，抗压能力等心理能力。
2. 不要涉及各类证书（比如英语四六级，日语N1-N5等）或论文要求。
3. 不要涉及学历或学位要求（比如硕士，博士，大专，本科）。
4. 不要涉及与专业技能无关的描述，比如福利待遇，企业文化等。
请阅读完岗位详情后逐条列举，不要遗漏。要求语言简洁，尽量使用原文，并且不要包含思考过程和其他内容。

"""
    try:
        response = client.chat.completions.create(
            model="Qwen2.5-3B",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100,
        )
        result = response.choices[0].message.content.strip()
        return result

    except Exception as e:
        print(f"调用模型出错: {e}")
        return []

def preprocess_ability(loc_df):
    if '岗位详情' not in loc_df.columns:
        print("错误：未找到‘岗位详情’列")
        return loc_df

    tqdm.pandas(desc="岗位详情")
    loc_df['能力要求'] = loc_df['岗位详情'].progress_apply(tool_ability_coding)
    return loc_df
