import openai
from tqdm import tqdm

def tool_study_coding(text):

    client = openai.OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY"
    )

    # 构造prompt
    prompt = f"""
你是一个专业的信息提取助手。现在有如下岗位详情：
{text}

请阅读该岗位详情，并判断该岗位对应聘人的学习能力的要求，分为0~4五档：
0：岗位的业务没有什么难度，不需要任何学习能力
1：岗位的业务涉及一定专业知识，需要一定的学习能力
2：岗位的业务涉及大量专业知识，可能涉及开发，研发，科创等，需要较高的学习能力
3：岗位的业务涉及大量高深的专业知识，可能涉及尖端产业的开发，研发，科创等，需要极高的学习能力
最后输出为0~4中的一个整数
注意：
注意：只输出一个整数，不要输出思考过程，不要输出任何解释。

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
        if result in [0,1,2,3,4,5]:
            return result
        else:
            return 0

    except Exception as e:
        print(f"调用模型出错: {e}")
        return 0

def preprocess_study(loc_df):
    if '岗位详情' not in loc_df.columns:
        print("错误：未找到‘岗位详情’列")
        return loc_df

    tqdm.pandas(desc="岗位详情")
    loc_df['学习要求'] = loc_df['岗位详情'].progress_apply(tool_study_coding)

    return loc_df
