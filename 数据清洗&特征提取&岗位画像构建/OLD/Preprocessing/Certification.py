import openai
from tqdm import tqdm

def tool_certification_coding(text):

    client = openai.OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY"
    )

    # 构造prompt
    prompt = f"""
你是一个专业的信息提取助手。现在有如下岗位详情：
{text}

请从中提取出岗位所需的所有证书或论文要求，包括但不限于：
1. 英语的四级（CET-4），六级（CET-6）；日语的N1-N5等。
2. 各个岗位，技能的证书（如律师资格证，教师资格证，计算机二级等）。
3. CCF，SCI，Nature等期刊，会议。
请注意：
请阅读完岗位详情后逐条列举，不要遗漏。要求直接使用原文的说法，不要输出思考过程，不要输出任何解释。
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

def preprocess_certification(loc_df):
    if '岗位详情' not in loc_df.columns:
        print("错误：未找到‘岗位详情’列")
        return loc_df

    tqdm.pandas(desc="岗位详情")
    loc_df['证书论文要求'] = loc_df['岗位详情'].progress_apply(tool_certification_coding)
    return loc_df
