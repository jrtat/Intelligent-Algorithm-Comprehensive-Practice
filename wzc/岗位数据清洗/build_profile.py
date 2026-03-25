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

def build_job_profile(client, job_name, job_details, company_traits, industry, model_manager):
    system_prompt = """你是一个专业的图谱知识抽取引擎。你的任务是根据输入的招聘JD信息（岗位详情、公司特质、所属行业），抽取高度结构化的JSON岗位画像。

输出的数据结构必须严格遵守以下JSON Schema：
{
  "profile_type": "JOB_POSTING",
  "title": "岗位名称",
  "hard_skills": [
    {"skill_name": "技能名称", "category": "编程语言/框架/工具/理论"}
  ],
  "certifications": ["证书名称1", "证书名称2"],
  "soft_skills": {
    "innovation": {"score": 1, "evidence": "原句"},  // score 范围 1-5
    "learning": {"score": 1, "evidence": "原句"},    // score 范围 1-5
    "stress_tolerance": {"score": 1, "evidence": "原句"}, // score 范围 1-5
    "communication": {"score": 1, "evidence": "原句"}   // score 范围 1-5
  },
  "experience": {
    "internship_priority": true, // 是否优先有大厂或对口实习经历
    "core_module_depth": "处理用户咨询和解答问题"  //  期望求职者参与核心模块的程度  
  },
  "domain_preference": ["领域1", "领域2"]
}

【强制打分基准 (1-5分)】：
1. **抗压能力**：
   - 5分：明确指出996、支撑大促级高并发高可用、高危系统保障、极强心理承受力。
   - 3分：日常业务抗压、应对进度压力。
   - 1分：明确不加班或完全无压力描述。
2. **创新能力**：
   - 5分：明确要求技术攻坚储备、主导架构升级优化、提供颠覆性解决方案。
   - 3分：日常系统优化、关注最新技术。
   - 1分：执行既定方案、无自主创新要求。
3. **学习能力**：
   - 5分：需快速上手跨领域前沿技术、阅读顶会论文、公司由实验室/科研院所组成。
   - 3分：良好的自学能力、能跟进行业动态。
   - 1分：掌握现有框架即可，无需额外探索。
4. **沟通能力**：
   - 5分：频繁跨部门拉通协作、主导技术方案陈述/报告、协调多方资源。
   - 3分：基本团队配合、需求对接。
   - 1分：独立开发为主、极少协作。

注意：
- 若原文没有提及软技能，请结合岗位常识给定合理底线分数及推断依据。
- 请直接输出合法的纯JSON字符串，不要输出markdown语法（如```json），不要带有任何解释文字。"""

    user_prompt = f"""岗位名称：{job_name}
所属行业：{industry}
公司特质：{company_traits}
岗位详情：{job_details}"""

    while True:
        current_model = model_manager.get_current_model()
        if not current_model:
            print("可用模型已全部耗尽！跳过该数据抽取。")
            return None
            
        try:
            response = client.chat.completions.create(
                model=current_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.01
            )
            result_str = response.choices[0].message.content.strip()
            
            # 手动清理 markdown 包裹以确保能成功 load
            if result_str.startswith("```json"):
                result_str = result_str[7:]
            elif result_str.startswith("```"):
                result_str = result_str[3:]
                
            if result_str.endswith("```"):
                result_str = result_str[:-3]
                
            json_data = json.loads(result_str.strip())
            return json_data
            
        except json.JSONDecodeError as e:
            print(f"[!] 模型 {current_model} 输出的不是合法JSON格式 (Parse Error: {e})。内容片段：{result_str[:50]}...")
            # 因为不是合理的JSON，可能是模型能力不够或Token截断，切换下一个模型
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
        
    # 读取预分配的模型列表
    models_env = os.getenv("DASHSCOPE_MODELS", "qwen-plus,qwen-turbo,qwen-long")
    model_manager = ModelManager(models_env)
    print(f"配置文件已加载，预备模型列表: {model_manager.models}")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    input_path = os.path.join(base_dir, 'data', 'job_tollm.xlsx')
    output_path = os.path.join(base_dir, 'data', 'job_profiles.jsonl')
    
    if not os.path.exists(input_path):
        print(f"Error: 找不到数据文件 {input_path}")
        return
        
    print(f"正在读取合并版输入文件: {input_path}")
    df = pd.read_excel(input_path)
    total_rows = len(df)
    
    print("\n========= 开始批量生成静态岗位画像 JSON =========")
    
    # 我们将结果保存为 jsonl 格式（JSON Lines），非常方便未来向 Neo4j 或大模型引擎直接并行导入
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, row in df.iterrows():
            job_name = row.get('岗位名称', '')
            industry = row.get('所属行业', '')
            company_traits = row.get('公司特质', '')
            job_details = row.get('岗位详情', '')
            
            print(f"[{idx+1}/{total_rows}] 抽取岗位画像: {job_name} (当前模型:{model_manager.get_current_model()})")
            
            profile_json = build_job_profile(
                client, job_name, job_details, company_traits, industry, model_manager
            )
            
            if profile_json:
                # 写入 json lines
                f.write(json.dumps(profile_json, ensure_ascii=False) + '\n')
            
            # API 频率限制缓冲，按用户习惯加点延迟
            time.sleep(1)
            
    print(f"\n✅ 所有处理完成！结构化 JSON 岗位画像已保存至: {output_path}")

if __name__ == "__main__":
    main()
