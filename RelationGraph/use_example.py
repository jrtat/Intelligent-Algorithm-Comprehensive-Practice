from RelationGraph.func.use.use_lora_model import predict_probabilities


if __name__ == "__main__":
    result = predict_probabilities("""
    {
  "name": "陈程",
  "age": "32",
  "education": "硕士",
  "major": "计算机科学与技术",
  "skills": [
    "精通 C/C++",
    "熟悉 Linux 环境开发",
    "掌握多线程/网络编程",
    "掌握内存管理与性能优化",
    "了解 Python、Go 语言",
    "熟练使用 VS、CLion、GCC、Makefile、Git、SVN",
    "熟悉 GDB/Valgrind 调试",
    "扎实的数据结构与算法功底"
  ],
  "certificates": [
    "大学英语六级（CET6）"
  ],
  "projectExperience": [
    "主导高性能服务端组件底层核心模块重构",
    "参与分布式存储系统设计，提升吞吐量与稳定性",
    "参与搜索引擎底层索引模块开发与查询响应速度优化",
    "参与服务器框架迭代，提升并发处理能力",
    "参与游戏后台服务模块开发与日志系统优化"
  ],
  "internshipExperience": [
    "腾讯科技（北京）有限公司 后台开发部 / C/C++ 开发实习生：参与游戏后台服务模块开发、接口调试、日志系统优化，学习工程化规范与代码评审流程"
  ],
  "practicalExperience": [
    "西安电子科技大学 校级优秀毕业生",
    "程序设计竞赛一等奖",
    "多次获得专业奖学金"
  ],
  "hobbies": [
    "算法竞赛",
    "嵌入式开发",
    "骑行",
    "技术博客写作",
    "羽毛球"
  ],
  "summary": "具备扎实的计算机理论基础与深厚的 C/C++ 功底，擅长底层开发、性能调优与问题排查；具备大型分布式项目实战经验，工程能力强、代码规范；学习能力突出，抗压性好，注重团队协作与技术沉淀。",
  "other": "生日：1992.08.15；现居：北京海淀；电话：138 8888 8888；邮箱：1234567898@qq.com；国家统考统招双证硕士；专注嵌入式系统开发与高性能计算",
  "targetRole": "C/C++开发工程师",
  "completeness": 92.0,
  "scores": {
    "adaptability": 88.0,
    "technicalDepth": 94.0,
    "communication": 82.0,
    "stressTolerance": 90.0,
    "innovation": 85.0
  },
  "scoreExplanations": {
    "completeness": "教育、工作、实习、技能、证书、自我评价等关键模块齐全，信息详实，仅少量格式瑕疵，完整度高。",
    "technicalDepth": "深耕C/C++多年，覆盖底层开发、性能优化、分布式系统、内存管理、调试工具链，具备系统级工程能力，技术纵深突出。",
    "adaptability": "横跨字节、百度、腾讯三大厂，涉及搜索、存储、游戏等多元场景，快速适配不同技术栈与协作模式，适应力强。",
    "communication": "自我评价强调团队协作与技术沉淀，实习中参与代码评审流程，但缺乏具体跨角色协作案例佐证。",
    "stressTolerance": "支撑亿级用户场景、主导核心模块重构、高频崩溃修复等经历明确体现强抗压性与交付韧性。",
    "innovation": "算法竞赛获奖、技术博客写作、嵌入式兴趣及参与系统级重构与优化，展现持续技术探索与改进意识。",
    "competitiveness": "综合实力强劲，技术深度与工程经验均达中高级工程师水准，就业竞争力优秀，适合核心系统岗或技术专家路径。"
  }
}   
    """)
    # 按概率降序查看前5个最可能的职业
    top5 = sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]
    for job, prob in top5:
        print(f"{job}: {prob:.4f}")