from sklearn.model_selection import cross_val_predict
from RelationGraph.func.utils.calc_matrix import build_matrix

def rf_calc_proba(rf_clf, x_fused, y, class_names):
    proba = cross_val_predict(
        rf_clf,
        x_fused,
        y,
        cv=5,
        method='predict_proba',
        n_jobs=-1
    ) # 使用 cross_val_predict 获取每个样本的预测概率
    return build_matrix(proba, y, class_names)