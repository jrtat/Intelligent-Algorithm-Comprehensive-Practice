from sklearn.ensemble import RandomForestClassifier
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

def get_rf(x_train, y_train):
    rf_clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=30,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf_clf.fit(x_train, y_train)
    return rf_clf

def rf_predict_proba(rf_clf, x_test):
    proba_rf_test = rf_clf.predict_proba(x_test)
    return proba_rf_test

def rf_evaluate(proba_rf_test,y_test):
    pred_rf_test = np.argmax(proba_rf_test, axis=1)
    rf_acc = accuracy_score(y_test, pred_rf_test)
    rf_f1 = f1_score(y_test, pred_rf_test, average='macro')
    print(f"RandomForest 测试集结果 | Accuracy: {rf_acc:.4f} | Macro F1: {rf_f1:.4f}")