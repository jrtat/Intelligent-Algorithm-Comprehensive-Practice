
from pandas import DataFrame
from tqdm import tqdm

class ExcelMaker:
    def __init__(self, file_name):
        self.file_name = file_name

    def save_job(self, data): # data为json格式

        df = DataFrame(columns=["id", "name", "company", "city", "salary", "description", "source", "education_1",
                                "education_2", "创新能力", "抗压能力", "沟通能力", "学习能力", "实习能力", "职业技能", "证书要求"])

        for key in tqdm(data.keys(), desc="正在处理数据.."):

            if "key_info" in data[key]:
                if data[key]["key_info"]:
                    for k, v in data[key]["key_info"].items():
                        if isinstance(v, list):
                            data[key][k] = ",".join(v)
                        else:
                            data[key][k] = v
                data[key].pop("key_info")

            for col in df.columns:
                if col not in data[key]:
                    data[key][col] = ""

            df.loc[len(df)] = [key, data[key]["name"], data[key]["company"], data[key]["city"], data[key]["salary"],
                               data[key]["description"], data[key]["source"], data[key]["education_1"],
                               data[key]["education_2"], data[key]["创新能力"], data[key]["抗压能力"],
                               data[key]["沟通能力"], data[key]["学习能力"], data[key]["实习能力"], data[key]["职业技能"],
                               data[key]["证书要求"]]

        df.to_excel(self.file_name, index=False)
