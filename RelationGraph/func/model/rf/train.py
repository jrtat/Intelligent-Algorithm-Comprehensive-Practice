from sklearn.ensemble import RandomForestClassifier

def get_rf(x_train, y_train):
    rf_clf = RandomForestClassifier(
        n_estimators=250,
        max_depth=80,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf_clf.fit(x_train, y_train)
    return rf_clf