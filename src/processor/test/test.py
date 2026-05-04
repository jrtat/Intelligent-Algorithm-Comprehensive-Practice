# # # import pandas as pd
# # #
# # # df = pd.read_excel('data.xls')
# # # print(df["岗位详情"].head())
# # # df["岗位详情"] = df["岗位详情"].replace("<br>", "")
# # # df["岗位详情"] = df["岗位详情"].replace(r"<[^>]+>", "", regex=True)  # 移除所有HTML标签
# # # print(df["岗位详情"].head())
# # #
# # # print(df["所属行业"].head())
# # # df['所属行业'] = list(set(str(df['所属行业']).split(',')))
# # # print(df["所属行业"].head())
# # from processor.utils.FileProcessor import FileProcessor
# # #
# # # fp = FileProcessor("test/test.json")
# # # fp.save(data={"a": 1, "b": 2})
# # # import os
# # #
# # from KnowledgeGraph.func.use_graph.cypher_search import Searcher
# # from KnowledgeGraph.func.use_graph.get_context import ContextGetter
# # from KnowledgeGraph.func.utils.conn_neo4j import connect_neo4j
# # from KnowledgeGraph.func.utils.get_models import get_local_embedding
# # from processor.utils.FileProcessor import FileProcessor
# # from tqdm import tqdm
# #
# #
# # graph = connect_neo4j()
# # print(graph.query("MATCH (n) RETURN n LIMIT 10"))
# #
# # # fp = FileProcessor("result.json")
# # # dic = fp.read()
# # # fp_new = FileProcessor("result_new.json")
# # # dic_new = fp_new.read()
# #
# {
#   "candidate_name":string,
#   "target_job":string,
#   "candidate_summary": {
#     "current_background":string,
#     "core_strengths":string[],
#     "areas_for_improvement":string[]
#   },
#   "match_analysis": {
#     "skill_match_score":number,
#     "experience_match_score":number,
#     "education_fit":string,
#     "overall_match_score":number,
#     "match_level":string
#   },
#   "gap_analysis": {
#     "hard_skills_gaps": [
#       {
#         "skill":string,
#         "importance":string,
#         "current_level":string,
#         "target_level":string,
#         "learning_resources":string[]
#       }
#     ],
#     "soft_skills_gaps": [
#     {
#         "skill":string,
#         "importance":string,
#         "current_level":string,
#         "target_level":string,
#         "learning_resources":string[]
#       }
#     ],
#     "experience_gaps": [
#     {
#         "skill":string,
#         "importance":string,
#         "current_level":string,
#         "target_level":string,
#         "learning_resources":string[]
#       }, ... # 结构体列表
#     ],
#     "certification_needs":string[]
#   },
#   "career_path_planning": {
#     "career_goals": {
#       "short_term": {
#         "duration":string,
#         "goal_description":string,
#         "key_milestones":string[],
#         "success_criteria":string[]
#       },
#       "mid_term": {
#         "duration":string,
#         "goal_description":string,
#         "key_milestones":string[],
#         "success_criteria":string[]
#       },
#       "long_term": {
#         "duration":string,
#         "goal_description":string,
#         "key_milestones":string[],
#         "success_criteria":string[]
#       }
#     },
#     "industry_trends": {
#       "social_demand":string,
#       "technology_trends":string,
#       "market_changes":string,
#       "salary_trends":string"
#     },
#     "development_path": {
#       "path_stages": [
#         {
#           "stage_name":string,
#           "level":number,
#           "typical_duration":string,
#           "core_requirements":string[],
#           "key_responsibilities":string[],
#           "promotion_criteria":string
#         },
#         {
#           "stage_name":string,
#           "level":number,
#           "typical_duration":string,
#           "core_requirements":string[],
#           "key_responsibilities":string[],
#           "promotion_criteria":string
#         },
#         {
#           "stage_name":string,
#           "level":number,
#           "typical_duration":string,
#           "core_requirements":string[],
#           "key_responsibilities":string[],
#           "promotion_criteria":string
#         }, ... # 结构体列表
#       ],
#       "alternative_paths": [
#         {
#           "path_name":string,
#           "description":string,
#           "transition_requirements":string[]
#         }, ... # 结构体列表
#       ]
#     }
#   },
#   "development_plan": {
#     "phase_1": {
#       "duration":string,
#       "goals":string[],
#       "actions":string[],
#       "milestones":string[]
#     },
#     "phase_2":  {
#       "duration":string,
#       "goals":string[],
#       "actions":string[],
#       "milestones":string[]
#     },
#     "phase_3":  {
#       "duration":string,
#       "goals":string[],
#       "actions":string[],
#       "milestones":string[]
#     },
#     "phase_4":  {
#       "duration":string,
#       "goals":string[],
#       "actions":string[],
#       "milestones":string[]
#     }
#   },
#   "action_plan": {
#     "short_term_plan": {
#       "duration":string,
#       "learning_path": {
#         "courses":string[],
#         "books":string[],
#         "online_resources":string[],
#         "expected_outcomes":string[]
#       },
#       "practice_arrangements": {
#         "projects":string[],
#         "internships":string,
#         "competitions":string[],
#         "expected_outcomes":string[]
#       },
#       "certifications":string[],
#       "quantifiable_goals": [
#         {
#           "metric":string,
#           "target_value":string,
#           "measurement_method":string
#         }, ... # 结构体列表
#       ]
#     },
#     "mid_term_plan": {
#       "duration":string,
#       "advanced_learning": {
#         "advanced_courses":string[],
#         "professional_training":string[],
#         "expected_outcomes":string[]
#       },
#       "project_experience": {
#         "independent_projects":string[],
#         "team_projects":string[],
#         "portfolio_building":string,
#         "expected_outcomes":string[]
#       },
#       "industry_engagement": {
#         "conferences":string[],
#         "tech_meetups":string[],
#         "networking":string,
#         "mentorship":string
#       },
#       "quantifiable_goals": [
#         {
#           "metric":string,
#           "target_value":string,
#           "measurement_method":string
#         }
#       ]
#     },
#     "evaluation_framework": {
#       "evaluation_cycles": {
#         "self_assessment":string,
#         "deep_review":string,
#         "annual_review":string
#       },
#       "quantitative_metrics": [
#         {
#           "metric_name":string,
#           "scale":string,
#           "assessment_method":string,
#           "target_progression":string
#         },
#         {
#           "metric_name":string,
#           "unit":string,
#           "assessment_method":string,
#           "target_progression":string
#         },
#         {
#           "metric_name":string,
#           "unit":string,
#           "assessment_method":string,
#           "target_progression":string
#         },
#         {
#           "metric_name":string,
#           "scale":string,
#           "assessment_method":string,
#           "target_progression":string
#         },
#         {
#           "metric_name":string,
#           "scale":string,
#           "assessment_method":string,
#           "target_progression":string
#         }
#       ],
#       "dynamic_adjustment": {
#         "adjustment_triggers":string[],
#         "adjustment_process":string,
#         "feedback_loop":string
#       },
#       "risk_warning": {
#         "potential_obstacles":string[],
#         "early_warning_signs":string[],
#         "contingency_plans":string[]
#       }
#     }
#   },
#   "resource_recommendations": {
#     "courses":string[],
#     "books":string[],
#     "projects":string[],
#     "communities":string[]
#   },
#   "risk_assessment": {
#     "major_risks":string[],
#     "mitigation_strategies":string[],
#     "backup_plans":string[]
#   },
#   "success_probability": {
#     "probability_percentage":number,
#     "key_factors":string[],
#     "improvement_suggestions":string[]
#   },
#   "final_recommendation":string
# }
#
#  #
# # # for i in dic:
# # #     for j in dic[i]:
# # #         dic_new[i][j] = dic[i][j]
# # #
# # # fp_new.write(dic_new)
