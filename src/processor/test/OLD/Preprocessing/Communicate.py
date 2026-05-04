import openai
from tqdm import tqdm

def tool_communicate_coding(text):

    client = openai.OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY"
    )

    # 构造prompt
    prompt = f"""
你是一个专业的信息提取助手。现在有如下岗位详情：
{text}

请阅读该岗位详情，并判断该岗位对“沟通能力”（包含需要长期团队协作，与客户交流，管理一个部门等）的要求，分为0~3四档：
0：不需要沟通能力（比如岗位信息没有提到任何与团队协作，沟通，交流相关的内容）
1：需要一定的沟通能力，多数人都具有这种能力
2：需要较高的沟通能力，能够管理协调15人左右的团队，与少量客户沟通协调
3：需要极高的沟通能力，能够管理协调一个大的部门，同时与许多客户沟通协调
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

def preprocess_communicate(loc_df):
    if '岗位详情' not in loc_df.columns:
        print("错误：未找到‘岗位详情’列")
        return loc_df

    tqdm.pandas(desc="岗位详情")
    loc_df['创新要求'] = loc_df['岗位详情'].progress_apply(tool_communicate_coding)

    return loc_df
