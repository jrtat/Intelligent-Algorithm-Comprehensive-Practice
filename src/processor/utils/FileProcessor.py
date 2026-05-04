# 统一文件读写
import json

class FileProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def read(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.data = data
        return data

    def write(self, data = None):
        if data:
            self.data = data
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def converter(self, obj):
        if isinstance(obj, set): # 去重的
            return list(obj)

        if isinstance(obj, dict):
            return {key: self.converter(value) for key, value in obj.items()}

        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                # if key.startswith('_'):
                #     continue
                result[key] = self.converter(value)
            return result

        # 其他类型尝试直接返回
        return obj

    def save(self, data = None):
        if data:
            self.data=self.converter(data)
        self.write(self.data)

    def copy(self, file_path):
        self.file_path = file_path
        self.save()