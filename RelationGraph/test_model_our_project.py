from RelationGraph.func.model.lora.use import predict_probabilities, lora_calc_proba
from RelationGraph.func.utils.config import dataset_path

from datasets import DatasetDict, concatenate_datasets

# Step 1：取出数据
dataset = DatasetDict.load_from_disk(dataset_path)
combined_dataset = concatenate_datasets([
    dataset['train'],
    dataset['validation'],
    dataset['test']
])
texts = combined_dataset['text']
y = combined_dataset['label_id']

# Step 2：计算亲缘矩阵
lora_calc_proba(texts, y)

# Step 2：例子
result = predict_probabilities("""
{
  "name": "刘伯温",
  "age": "25",
  "education": "硕士",
  "major": "工商管理（MBA）",
  "skills": [
    "精通数据库、C++ 及 Java",
    "熟练使用 Office 办公软件",
    "Axure RP",
    "Visio"
  ],
  "certificates": [
    "大学英语六级（CET6）"
  ],
  "projectExperience": [
    "作为项目经理建设海外某国华为全球培训中心",
    "主持华为大学交付流程开发设计",
    "华为培训 IT 系统开发设计",
    "领导力/员工技能交付方案设计"
  ],
  "internshipExperience": [
    "在HOYOMIX公司运营部门担任运营助理实习生期间，协助团队完成日常新媒体内容运营、用户数据整理及活动执行工作。负责公众号、短视频平台的素材搜集、文案初稿撰写与排版发布，累计参与产出内容 30 余篇；每日统计平台阅读量、互动率、粉丝增长等数据，整理成可视化报表，为内容优化提供参考；配合策划线上小型推广活动，参与用户沟通、奖品发放及活动复盘，有效提升账号活跃度与粉丝留存。实习中熟练掌握办公软件与基础运营工具，培养了较强的执行力、细节意识和跨岗位协作能力，能够高效完成团队交办的各项任务。"
  ],
  "practicalExperience": [
    "西北大学学生会主席"
  ],
  "hobbies": "画画、唱歌、跳舞",
  "summary": "工作积极认真，细心负责，熟练运用办公自动化软件，善于在工作中提出问题、发现问题、解决问题，有较强的分析能力；勤奋好学，踏实肯干，动手能力强，认真负责，有很强的社会责任感；坚毅不拔，吃苦耐劳，喜欢和勇于迎接新挑战。",
  "other": "生日：1989.05.07；现居：上海浦东；电话：136 6666 6666；邮箱：13666666@qq.com；籍贯未提；婚姻状况未提；粤语能力；国家统考统招双证MBA；全日制学籍但周末上课；陕西省优秀大学毕业生；国家一等奖学金获得者；优秀学生干部",
  "completeness": 72.0,
  "scores": {
    "adaptability": 78.0,
    "technicalDepth": 65.0,
    "communication": 75.0,
    "stressTolerance": 82.0,
    "innovation": 68.0
  },
  "scoreExplanations": {
    "completeness": "教育、工作经历详实，但缺少明确项目成果数据、证书细节及兴趣爱好，完整性中等偏上。",
    "technicalDepth": "虽列‘精通数据库、C++及Java’，无实际工程佐证，深度存疑。",
    "adaptability": "横跨培训体系搭建、跨国项目落地、多层级团队管理，体现强环境适配与角色转换能力。",
    "communication": "长期担任讲师、PD、部门负责人，需高频跨部门协同，结合自我评价中‘善于发现问题、解决问题’，沟通能力扎实。",
    "stressTolerance": "主导全球培训中心建设、多项目群管理、总部部门一把手经历，直面高压力复杂场景，抗压能力突出。",
    "innovation": "参与流程与IT系统设计、交付方案创新，但缺乏方法论沉淀或专利/成果量化描述，创新体现中等。",
    "competitiveness": "具备标杆企业全周期HR相关经验、全球化视野与体系化能力，匹配人力资源主管岗位，竞争力较强，建议补强组织发展（OD）与HRBP实操案例。"
  }
}
""")

# 按概率降序查看前5个最可能的职业
top5 = sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]
for job, prob in top5:
    print(f"{job}: {prob:.4f}")
