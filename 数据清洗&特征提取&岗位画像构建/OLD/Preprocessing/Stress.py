import openai
from tqdm import tqdm

def tool_stress_coding(text):

    client = openai.OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY"
    )

    # 构造prompt
    prompt = f"""
你是一个专业的信息提取助手。现在有如下岗位详情：
{text}

请阅读该岗位详情，并判断该岗位对“抗压能力”（包含高强度工作，或者与他人高强度交流等）的要求，分为0-3四档：
0：工作强度低，不会出现加班，且与他人交流少
1：工作强度普通，很少出现加班，可能涉及与他人沟通，但对方态度往往比较温和
2：工作强度较高，在忙的时候总是会出现加班，涉及与他人沟通，且对方可能情绪激动或者态度较差
3：工作强度极高，加班是常态，涉及与他人沟通，且对方总是情绪激动且态度极差
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

def preprocess_stress(loc_df):
    if '岗位详情' not in loc_df.columns:
        print("错误：未找到‘岗位详情’列")
        return loc_df

    tqdm.pandas(desc="岗位详情")
    loc_df['创新要求'] = loc_df['岗位详情'].progress_apply(tool_stress_coding)
    return loc_df
