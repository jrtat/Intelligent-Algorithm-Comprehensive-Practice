import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict
from xgboost import XGBClassifier
from tqdm import tqdm

def xgboost_calc_proba(x_fused, y):

    xgb_clf = XGBClassifier(
        n_estimators=300,
        max_depth=25,
        learning_rate=0.1,  # XGBoost 特有的学习率
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        eval_metric='mlogloss'
    )

    proba = cross_val_predict(
        xgb_clf,
        x_fused,
        y,
        cv=5,
        method='predict_proba',
        n_jobs=-1
    )

    return proba
