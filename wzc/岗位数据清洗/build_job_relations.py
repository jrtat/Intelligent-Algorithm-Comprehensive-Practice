import pandas as pd
import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

class ModelManager:
    def __init__(self, models_str):
        if models_str and models_str.strip():
            self.models = [m.strip() for m in models_str.split(',')]
        else:
            self.models = ["qwen-plus"]
        self.current_idx = 0
        
    def get_current_model(self):
        if self.current_idx < len(self.models):
            return self.models[self.current_idx]
        return None
        
    def advance_model(self):
        self.current_idx += 1

def build_relations(client, jobs_list, model_manager):
    system_prompt = """你是一个高级的职业发展与人才规划领域专家。你的任务是根据提供的一系列【岗位名称】列表，为它们建立未来发展路径（Neo4j知识图谱所需的Node和Edge关系）。

输出必须是一份完全合法、可被直接解析的纯JSON字符串。不要带```json 等前缀或后缀。

必须输出如下格式：
{
  "job_relations": [
    {
      "job_name": "必须是输入列表里的某个岗位",
      "description": "涵盖该岗位的核心工作描述（约50字）",
      "promotes_to": [
        {
          "target_job": "目标岗位(最好是列表中的，如果列表中没有则合理推断更高一阶的岗位)",
          "reason_for_promotion": "晋升路径关联信息与能力提升原因"
        }
      ],
      "transitions_to": [
        {
          "target_job": "目标岗位(必须是强相关的平调、换岗或跨界转型)",
          "reason_for_transition": "换岗血缘关系及转型路线可行性分析"
        }
      ]
    }
  ]
}

【强制要求】：
1. 涵盖所有具有代表性的软件与技术服务岗位，但为了满足要求：你【必须至少规划 5 个具有代表性的技术或业务岗位】。你也可以处理提供的全部岗位。
2. 针对这至少 5 个岗位，【每一个岗位的 `transitions_to` 数组必须不少于 2 条换岗路径】！这是铁律。
3. `promotes_to` 代表垂直晋升路径，可以有 1 到 2 条。
4. 全程不准带有任何 Markdown 语法、不要前缀输出。只能返回合法经过严格 JSON 校验的数据。"""

    user_prompt = f"以下是当前我们拥有的岗位名称列表：\n{jobs_list}"

    while True:
        current_model = model_manager.get_current_model()
        if not current_model:
            print("可用模型已全部耗尽！跳过图谱关系构建。")
            return None
            
        try:
            response = client.chat.completions.create(
                model=current_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            result_str = response.choices[0].message.content.strip()
            
            # 手动清理 markdown 块
            if result_str.startswith("```json"):
                result_str = result_str[7:]
            elif result_str.startswith("```"):
                result_str = result_str[3:]
                
            if result_str.endswith("```"):
                result_str = result_str[:-3]
                
            # 解析校验
            json_data = json.loads(result_str.strip())
            return json_data
            
        except json.JSONDecodeError as e:
            print(f"[!] 模型 {current_model} 输出非合法JSON格式。Parse Error: {e}")
            model_manager.advance_model()
        except Exception as e:
            print(f"[!] 模型 {current_model} 调用错误：{e}")
            model_manager.advance_model()

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(os.path.dirname(base_dir), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv(os.path.join(base_dir, '.env'))
        
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("====== 错误 ======")
        print("未找到 DASHSCOPE_API_KEY！请在 .env 中进行配置。")
        return
        
    models_env = os.getenv("DASHSCOPE_MODELS", "qwen-plus,qwen-turbo,qwen-long")
    model_manager = ModelManager(models_env)
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    # 提取唯一的岗位名称
    input_path = os.path.join(base_dir, 'data', 'job_tollm.xlsx')
    output_path = os.path.join(base_dir, 'data', 'job_relations_graph.json')
    
    if not os.path.exists(input_path):
        print(f"Error: 找不到数据文件 {input_path}")
        return
        
    print(f"读取岗位数据文件: {input_path}")
    df = pd.read_excel(input_path)
    jobs_list = list(df['岗位名称'].dropna().unique())
    print(f"共提取到 {len(jobs_list)} 个去重后的岗位种类。")
    
    print("\n--- 开始调用大语言模型构建【垂直与换岗血缘图谱】 ---")
    
    relations_json = build_relations(client, jobs_list, model_manager)
    
    if relations_json:
        # 直接美化输出保存为完整 json
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(relations_json, f, ensure_ascii=False, indent=2)
            
        print(f"\n✅ 岗位关联图谱 JSON 成功生成并保存至: {output_path}")
        print("您可以将此数据用于后续 Neo4j 图数据库的 Nodes 和 Edges 导入！")
    else:
        print("\n生成失败。")

if __name__ == "__main__":
    main()
