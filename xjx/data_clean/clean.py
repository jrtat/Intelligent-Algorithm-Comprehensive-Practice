# 提取相同岗位信息的共同特征、特殊要求和内在特征，构建关系，并构建不同岗位之间的关系


import json
import pandas as pd
from collections import defaultdict
import re
import jieba

# 加载清洗后的数据
with open('cleaned_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

jobs = data['jobs']
companies = data['companies']

# ========== 技能关键词库 ==========
SKILL_KEYWORDS = { # 这块需要根据实际数据调整
    '编程语言': ['Python', 'Java', 'C++', 'JavaScript', 'Go', 'SQL'],
    '框架': ['Spring', 'Django', 'Vue', 'React', 'TensorFlow', 'PyTorch'],
    '工具': ['Git', 'Docker', 'Kubernetes', 'Linux', 'MySQL', 'Redis'],
    '软技能': ['沟通能力', '团队合作', '学习能力', '抗压能力']
}

# 学历映射
EDUCATION_MAP = {
    '不限': 0, '大专': 1, '本科': 2, '硕士': 3, '博士': 4
}


class SkillExtractor:
    """技能和特征提取器"""

    def __init__(self):
        self.skills = {}
        self.education_levels = set()
        self.experience_levels = set()

    def extract_skills(self, text):
        """从文本中提取技能"""
        if not text:
            return []

        found_skills = []
        for category, keywords in SKILL_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    found_skills.append({
                        'name': keyword,
                        'category': category
                    })
        return found_skills

    def extract_education(self, text):
        """提取学历要求"""
        if not text:
            return '不限'

        for edu in ['博士', '硕士', '本科', '大专']:
            if edu in text:
                return edu
        return '不限'

    def extract_experience(self, text):
        """提取经验要求"""
        if not text:
            return '不限'

        patterns = [
            r'(\d+)年以上',
            r'(\d+)-(\d+)年',
            r'应届',
            r'无经验'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return '不限'

    def extract_salary_range(self, salary_str):
        """解析薪资范围"""
        if not salary_str:
            return {'min': 0, 'max': 0, 'unit': '月'}

        # 简单示例，可根据实际格式调整
        try:
            numbers = re.findall(r'\d+', str(salary_str))
            if len(numbers) >= 2:
                return {
                    'min': int(numbers[0]),
                    'max': int(numbers[1]),
                    'unit': '月'
                }
        except:
            pass

        return {'min': 0, 'max': 0, 'unit': '月'}


class KnowledgeGraphBuilder:
    """知识图谱构建器"""

    def __init__(self, jobs_data):
        self.jobs = jobs_data
        self.extractor = SkillExtractor()

        # 图谱节点
        self.job_nodes = {}
        self.skill_nodes = {}
        self.company_nodes = {}
        self.education_nodes = {}

        # 关系
        self.job_skill_relations = []
        self.job_company_relations = []
        self.job_education_relations = []
        self.skill_category_relations = []

    def build_graph(self):
        """构建知识图谱"""
        print("开始构建知识图谱...")

        # 按岗位名称分组
        job_groups = defaultdict(list)
        for job_id, job in self.jobs.items():
            job_groups[job['name']].append(job)

        # 处理每个岗位组
        for job_name, job_list in job_groups.items():
            self._process_job_group(job_name, job_list)

        print(f"✓ 构建了 {len(self.job_nodes)} 个岗位节点")
        print(f"✓ 提取了 {len(self.skill_nodes)} 个技能")
        print(f"✓ 建立了 {len(self.job_skill_relations)} 条关系")

        return self._export_graph()

    def _process_job_group(self, job_name, job_list):
        """处理同一岗位的多个实例"""

        # 聚合特征
        all_skills = []
        education_requirements = []
        experience_requirements = []
        salary_ranges = []

        for job in job_list:
            # 提取技能
            skills = self.extractor.extract_skills(job['description'])
            all_skills.extend(skills)

            # 提取学历
            edu = self.extractor.extract_education(job['requirement'])
            education_requirements.append(edu)

            # 提取经验
            exp = self.extractor.extract_experience(job['requirement'])
            experience_requirements.append(exp)

            # 提取薪资
            salary = self.extractor.extract_salary_range(job['salary'])
            salary_ranges.append(salary)

        # 创建岗位节点（聚合后的典型岗位）
        job_node = {
            'id': f"job_{job_name}",
            'name': job_name,
            'type': 'Job',
            'avg_salary_min': sum(s['min'] for s in salary_ranges) / len(salary_ranges) if salary_ranges else 0,
            'avg_salary_max': sum(s['max'] for s in salary_ranges) / len(salary_ranges) if salary_ranges else 0,
            'common_skills': list(set(s['name'] for s in all_skills)),
            'education_requirement': max(education_requirements,
                                         key=education_requirements.count) if education_requirements else '不限',
            'job_count': len(job_list)
        }

        self.job_nodes[job_name] = job_node

        # 建立技能关系
        for skill in set(s['name'] for s in all_skills):
            if skill not in self.skill_nodes:
                self.skill_nodes[skill] = {
                    'id': f"skill_{skill}",
                    'name': skill,
                    'type': 'Skill'
                }

            self.job_skill_relations.append({
                'from': job_node['id'],
                'to': f"skill_{skill}",
                'relation': 'REQUIRES_SKILL',
                'frequency': sum(1 for s in all_skills if s['name'] == skill)
            })

        # 建立公司关系
        for job in job_list:
            company_name = job['company']
            if company_name and company_name not in self.company_nodes:
                self.company_nodes[company_name] = {
                    'id': f"company_{company_name}",
                    'name': company_name,
                    'type': 'Company'
                }

            self.job_company_relations.append({
                'from': f"company_{company_name}",
                'to': job_node['id'],
                'relation': 'HIRES_FOR',
                'count': 1
            })

    def _export_graph(self):
        """导出图谱数据"""
        return {
            'nodes': {
                'jobs': list(self.job_nodes.values()),
                'skills': list(self.skill_nodes.values()),
                'companies': list(self.company_nodes.values())
            },
            'relations': {
                'job_skill': self.job_skill_relations,
                'company_job': self.job_company_relations
            }
        }


# ========== 主流程 ==========
def main():
    # 构建知识图谱
    graph_builder = KnowledgeGraphBuilder(jobs)
    graph_data = graph_builder.build_graph()

    # 保存为 JSON
    with open('knowledge_graph.json', 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)

    print("\n✓ 知识图谱已保存到 knowledge_graph.json")

    # 保存为 CSV 格式（便于 Neo4j 导入）
    # 节点文件
    pd.DataFrame(graph_data['nodes']['jobs']).to_csv('nodes_jobs.csv', index=False)
    pd.DataFrame(graph_data['nodes']['skills']).to_csv('nodes_skills.csv', index=False)
    pd.DataFrame(graph_data['nodes']['companies']).to_csv('nodes_companies.csv', index=False)

    # 关系文件
    pd.DataFrame(graph_data['relations']['job_skill']).to_csv('relations_job_skill.csv', index=False)
    pd.DataFrame(graph_data['relations']['company_job']).to_csv('relations_company_job.csv', index=False)

    print("✓ CSV 文件已生成（可用于 Neo4j 导入）")

    return graph_data


if __name__ == '__main__':
    graph_data = main()