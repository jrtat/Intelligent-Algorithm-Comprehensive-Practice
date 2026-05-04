from src.processor.utils.FileProcessor import FileProcessor

fp = FileProcessor("jobs.json")
dic = fp.read()

print(f"共有工作岗位信息{len(dic)}条")

c = 0

keys_study = ["学历要求", "毕业院校要求"]
keys_ability = ["创新能力", "抗压能力", "沟通能力", "学习能力", "实习能力"]

for i in dic:
    for j in keys_study:
        if not dic[i][j]:
            dic[i][j] = "无任何要求"
            c += 1
    for j in keys_ability:
        if dic[i][j] is None:
            dic[i][j] = 0
            c += 1
fp.write(dic)

print(c)