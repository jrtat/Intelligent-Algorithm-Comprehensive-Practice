import os
import json
import numpy as np

# ================ 配置文件 ================
SAVE_DIR = "results_bert"          # 结果保存目录
PROBA_FILE = "proba_bert.npy"      # 概率矩阵文件名
MATRIX_FILE = "affinity_bert.npy"  # 亲缘矩阵文件名
CLASSES_FILE = "class_names.json"  # 类别名称文件名
LABELS_FILE = "y_labels.npy"       # 标签文件名（可选）

def save_result(proba, affinity_matrix, class_names, y):
    """
    保存所有结果到指定目录。
    """
    global SAVE_DIR,PROBA_FILE,MATRIX_FILE,CLASSES_FILE,LABELS_FILE
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 保存数值矩阵 (使用 .npy 格式)
    np.save(os.path.join(SAVE_DIR, PROBA_FILE), proba)
    np.save(os.path.join(SAVE_DIR, MATRIX_FILE), affinity_matrix)
    np.save(os.path.join(SAVE_DIR, LABELS_FILE), y)

    # 保存类别名称列表 (JSON 格式)
    with open(os.path.join(SAVE_DIR, CLASSES_FILE), 'w', encoding='utf-8') as f:
        json.dump(class_names.tolist(), f, ensure_ascii=False, indent=2)

    print(f"结果已保存至: {SAVE_DIR}/")

def load_result(save_dir):
    """
    从指定目录加载已保存的结果。
    如果文件不存在则返回 None。
    """
    proba_path = os.path.join(save_dir, PROBA_FILE)
    matrix_path = os.path.join(save_dir, MATRIX_FILE)
    classes_path = os.path.join(save_dir, CLASSES_FILE)
    labels_path = os.path.join(save_dir, LABELS_FILE)

    if not all(os.path.exists(p) for p in [proba_path, matrix_path, classes_path, labels_path]):
        print("未找到完整的保存结果，将重新训练。")
        return None

    proba = np.load(proba_path)
    affinity_matrix = np.load(matrix_path)
    y = np.load(labels_path)

    with open(classes_path, 'r', encoding='utf-8') as f:
        class_names = np.array(json.load(f))

    print(f"已从 {save_dir}/ 加载已有结果。")
    return proba, affinity_matrix, class_names, y
