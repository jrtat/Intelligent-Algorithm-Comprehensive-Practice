from RelationGraph.func.utils.calc_top_k import top_k_accuracy

import numpy as np
from sklearn.metrics import accuracy_score, f1_score

def rf_predict_and_evaluate(rf_clf, x_test, y_test=None, verbose=True, top_k_list=None):
    proba = rf_clf.predict_proba(x_test)
    if y_test is not None:
        pred = np.argmax(proba, axis=1)
        acc = accuracy_score(y_test, pred)
        f1 = f1_score(y_test, pred, average='macro')
        if verbose:
            print(f"RandomForest 测试集结果 | Accuracy: {acc:.4f} | Macro F1: {f1:.4f}")
        if top_k_list is not None:
            topk = top_k_accuracy(proba, y_test, top_k_list)
            if verbose:
                for k, v in topk.items():
                    print(f"Top-{k} Accuracy: {v:.4f}")
            return proba, topk
    return proba