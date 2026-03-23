import openai
from tqdm import tqdm

def tool_practice_coding(text):

    client = openai.OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY"
    )

    # 构造prompt
    prompt = f"""
你是一个专业的信息提取助手。现在有如下岗位详情：
{text}

请阅读该岗位详情，并判断该岗位是否有实习的要求，分为0~3四档：
0：不需要有实习
1：需要有3个月以内的实习
2：需要有6个月以内的实习
3：需要有1年以内的实习
4：需要有1年以外的实习
最后输出为0~3中的一个整数
注意：
1. 注意是岗位对应聘者过往实习的需求，不是该岗位最少实习时间
2. 只输出一个整数，不要输出思考过程，不要输出任何解释。

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

def preprocess_practice(loc_df):
    if '岗位详情' not in loc_df.columns:
        print("错误：未找到‘岗位详情’列")
        return

    tqdm.pandas(desc="岗位详情")
    loc_df['创新要求'] = loc_df['岗位详情'].progress_apply(tool_practice_coding)

    return loc_df