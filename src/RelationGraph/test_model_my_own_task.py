from src.RelationGraph.func.utils.get_model import get_embedding_temp
from src.RelationGraph.func.prepare.get_data import get_data_raw
# from RelationGraph.func.prepare.init_data import init_data_raw
from src.RelationGraph.func.model.mlp.train import MLPClassifier
from src.RelationGraph.func.model.mlp.evaluate import predict_proba_dict
from src.RelationGraph.func.utils.config import personal_model_path1, personal_model_path2

import joblib
import torch
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') # 检测是否有gpu，如果有就用cuda

# Step 0：读取分类数据
df = get_data_raw()
X_fused = np.load("X_fused.npy")
le = LabelEncoder()
y = le.fit_transform(df['职业类别'])
class_names = le.classes_ # 保存编码器中的类别列表 class_names，用于后续映射

# Step 1：读取模型

#--- mlp ---#
checkpoint1 = torch.load(personal_model_path1, map_location=device) # 加载保存的字典
mlp_clf = MLPClassifier(
    input_dim=checkpoint1['input_dim'],
    num_classes=checkpoint1['num_classes'],
    hidden_dim=checkpoint1['hidden_dim']
).to(device) # 使用保存的超参数重新创建模型结构
mlp_clf.load_state_dict(checkpoint1['model_state_dict']) # 加载权重
mlp_clf.eval()  # 切换到评估模式

#--- mlp-all ---#
checkpoint2 = torch.load(personal_model_path2, map_location=device) # 加载保存的字典
mlp_all_clf = MLPClassifier(
    input_dim=checkpoint2['input_dim'],
    num_classes=checkpoint2['num_classes'],
    hidden_dim=checkpoint2['hidden_dim']
).to(device) # 使用保存的超参数重新创建模型结构
mlp_all_clf.load_state_dict(checkpoint2['model_state_dict']) # 加载权重
mlp_all_clf.eval()  # 切换到评估模式

# Step 2：存储为相似矩阵
# mlp_calc_proba(mlp_all_clf,device,X_fused,y,class_names)

# Step 3：用具体的例子测试
embedder = get_embedding_temp()
text = """
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
"""
embedding = embedder.embed_query(text)

result1 = predict_proba_dict(mlp_clf, embedding, device, class_names=class_names)
print("=== MLP Top 预测 ===")
result1_sorted = dict(sorted(result1.items(), key=lambda x: x[1], reverse=True))
for cls, prob in result1_sorted.items():
    print(f"{cls:10} : {prob:.4f}")

result2 = predict_proba_dict(mlp_all_clf, embedding, device, class_names=class_names)
print("=== MLP Top 预测 ===")
result2_sorted = dict(sorted(result2.items(), key=lambda x: x[1], reverse=True))
for cls, prob in result2_sorted.items():
    print(f"{cls:10} : {prob:.4f}")