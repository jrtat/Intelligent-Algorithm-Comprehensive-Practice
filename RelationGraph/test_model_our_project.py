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
# lora_calc_proba(texts, y)

# Step 2：例子
result = predict_probabilities("""
{
  "name": "吴悦",
  "age": "25",
  "education": "本科",
  "major": "通信工程",
  "skills": [
    "熟练使用Axure、Figma等原型工具",
    "精通产品文档编写（PRD、操作手册、迭代报告）",
    "具备数据分析能力（用户行为、转化数据统计与分析）",
    "熟练使用PS、AI等设计软件",
    "熟悉电商平台产品开发流程",
    "掌握新媒体内容策划与发布",
    "熟悉Xmind、Visio绘制流程图与思维导图",
    "熟练使用Office办公套件（Word、Excel、PowerPoint）",
    "掌握基础日语、韩语"
  ],
  "certificates": [
    "大学英语六级（CET-6）"
  ],
  "projectExperience": [
    "参与电商平台产品开发：需求调研、PRD撰写、原型评审、用户体验优化",
    "智能座舱产品基础工作：行业动态收集、用户需求整理、资料归档与方案梳理",
    "医疗技术推广产品落地：资料整理、推广素材制作、合作方对接与价值传递"
  ],
  "internshipExperience": [
    "广州唯品会信息科技有限公司 | 产品实习生 | 2021.07 - 2022.06",
    "广州迈瑞医疗电子股份有限公司 | 产品助理实习生 | 2020.07 - 2020.09"
  ],
  "practicalExperience": [
    "参与新媒体内容运营：产品相关内容策划、编辑与发布，支持用户增长目标",
    "协助多部门协同：需求传递、进度跟进、问题反馈与闭环"
  ],
  "hobbies": [
    "产品研究（电商/智能座舱/医疗前沿动态）",
    "原型设计练习",
    "数据分析实践",
    "新媒体内容策划",
    "多语言学习",
    "户外露营",
    "摄影",
    "读书（产品类书籍、行业期刊）"
  ],
  "summary": "具备2年以上产品助理相关工作经验，拥有通信工程本科学历，熟悉产品开发、运营全流程，具备扎实的产品基础技能与跨领域适配能力。工作积极主动、认真负责，具备较强的学习能力与抗压能力，能快速适应新产品、新领域；具备优秀的沟通协调与逻辑思维能力，秉持“用户为核心”的产品理念，致力于提升产品体验。",
  "other": "生日：1999.04.30；现居地：广州天河区；普通话标准流利；持有CET-6证书；掌握基础日语、韩语；无婚姻状况、籍贯等信息。",
  "targetRole": "产品专员/助理",
  "completeness": 92.0,
  "scores": {
    "adaptability": 88.0,
    "technicalDepth": 76.0,
    "communication": 90.0,
    "stressTolerance": 85.0,
    "innovation": 72.0
  },
  "scoreExplanations": {
    "completeness": "简历结构清晰、信息全面，涵盖教育、多段实习与全职经历、技能、证书、爱好及自我评价，仅缺部分细节如具体项目成果数据，完整度高。",
    "technicalDepth": "熟练掌握主流产品工具链与方法论，覆盖原型、文档、数据、设计、协同全流程，但缺乏复杂系统建模、AB测试深度实践或技术原理理解等高阶体现。",
    "adaptability": "明确展示跨电商、医疗、智能座舱三大领域经验，叠加多语言能力与快速学习表述，适应能力突出，有实证支撑。",
    "communication": "强调普通话流利、英文读写、跨部门协同、需求精准传递，并在多段经历中反复体现高效对接，沟通能力表现充分且具象。",
    "stressTolerance": "自我评价中明确提及‘抗压能力’并佐以2年全职+3段实习的高强度复合履历，含多线程任务推进，可信度高。",
    "innovation": "兴趣含产品研究与原型练习，但未呈现独立创新项目、用户洞察驱动的新功能提案或专利/方法论沉淀，创新体现偏执行层。",
    "competitiveness": "综合竞争力强，属优质初级产品人才，已具备企业即战力；建议补充量化成果（如某次优化提升转化率X%）与深度思考案例以冲刺中阶岗位。"
  }
}
""")

# 按概率降序查看前5个最可能的职业
top5 = sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]
for job, prob in top5:
    print(f"{job}: {prob:.4f}")