# 岗位匹配信息返回器
from processor.tools.Matcher import Matcher


# 读取简历信息和岗位信息 -> 整合成提示词 -> 得到评分 -> 取前三岗位类型 -> 分别得到各岗位类型的前三匹配信息 -> 返回

class JobSender:
    def __init__(self, path): # 需要所有岗位名称和岗位类型
        matcher = Matcher(path)
        

    def get_score(self):
        pass



