from sklearn.metrics import accuracy_score, f1_score
import numpy as np

def evaluate_proba(proba, y_true, method_name):
    """计算并打印准确率和宏平均 F1 分数"""
    pred = np.argmax(proba, axis=1) # 概率 → 硬标签
    acc = accuracy_score(y_true, pred)
    f1 = f1_score(y_true, pred, average='macro')
    print(f"{method_name:15s} | Accuracy: {acc:.4f} | Macro F1: {f1:.4f}")
    return acc, f1
