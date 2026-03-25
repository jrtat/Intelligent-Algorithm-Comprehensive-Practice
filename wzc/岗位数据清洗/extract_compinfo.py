import pandas as pd
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

class ModelManager:
    def __init__(self, models_str):
        # 预分配模型，按逗号分隔
        if models_str and models_str.strip():
            self.models = [m.strip() for m in models_str.split(',')]
        else:
            self.models = ["qwen-plus"] # 默认值
        self.current_idx = 0
        
    def get_current_model(self):
        if self.current_idx < len(self.models):
            return self.models[self.current_idx]
        return None
        
    def advance_model(self):
        self.current_idx += 1

def extract_company_traits(client, company_details_str, model_manager):
    if pd.isna(company_details_str) or not str(company_details_str).strip():
        return ""
        
    system_prompt = (
        "你是一个高度精炼的数据抽取专家。输入是多段公司详情，各段之间由'|'分隔。\n"
        "任务：概括出每家公司的“公司特质”。\n"
        "提取重点：重点关注公司是“研究院/实验室”、“互联网大厂”、“初创公司”、“国企/央企”、“外企”等特质，这有助于后续判断求职者的学术研究能力或抗压适应能力。\n"
        "要求：\n"
        "1. 必须使用'|'分隔每个公司的特质，且返回的特质数量严格对应输入的段落数量。\n"
        "2. 每段特质尽量简短精炼，用几个字概括（如“互联网大厂”、“科研院所”、“初创企业”、“上市名企”等）。\n"
        "3. 不要输出任何解释性文本、前缀或 markdown 格式块。"
    )
    
    user_prompt = f"输入:\n{str(company_details_str)}"
    
    # 获取可用模型并重试
    while True:
        current_model = model_manager.get_current_model()
        if not current_model:
            print("所有预分配的模型均已耗尽！跳过当前数据。")
            return ""
            
        try:
            response = client.chat.completions.create(
                model=current_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.04  # 使用极低的temperature确保输出稳定感觉还得加高一点
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"\n[!] 模型 {current_model} 调用失败: {e}")
            print(f"尝试切换到下一个模型...")
            model_manager.advance_model()

def main():
    # 上层目录找找.env，再在当前目录找找.env
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv() # 默认当前目录
        
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("====== 错误 ======")
        print("未找到 DASHSCOPE_API_KEY！")
        print("请在 .env 文件中进行配置，格式如下：\nDASHSCOPE_API_KEY=sk-你的阿里云百炼API_KEY")
        print("==================")
        return
        
    # 读取预分配的模型列表
    models_env = os.getenv("DASHSCOPE_MODELS", "qwen-plus,qwen-turbo,qwen-long")
    model_manager = ModelManager(models_env)
    print(f"已加载的预备模型列表: {model_manager.models}")
        
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, 'data', 'clean_job_group.xlsx')
    output_path = os.path.join(base_dir, 'data', 'job_tollm.xlsx')
    
    if not os.path.exists(input_path):
        print(f"找不到输入文件: {input_path}")
        return
        
    print(f"读取文件: {input_path}")
    df = pd.read_excel(input_path)
    total_rows = len(df)
    print(f"准备处理 {total_rows} 行数据")
    
    traits_list = []
    print("\n--- 开始调用大模型提取「公司详情」的公司特质 ---")
    
    # 因为调用 API 比较耗时且可能有频率限制，加入进度展示和微小延迟
    for index, row in df.iterrows():
        comp_info = row.get('公司详情', '')
        print(f"[{index + 1}/{total_rows}] 正在处理岗位: {row['岗位名称']} (当前模型: {model_manager.get_current_model()})")
        
        trait = extract_company_traits(client, comp_info, model_manager)
        traits_list.append(trait)
        
        # 按照用户的要求，可能睡2s
        time.sleep(2)
        
    # 添加新字段，移除旧字段
    df['公司特质'] = traits_list
    if '公司详情' in df.columns:
        df.drop(columns=['公司详情'], inplace=True)
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"\n处理完成！最终结果已成功保存至: {output_path}")

if __name__ == "__main__":
    main()
