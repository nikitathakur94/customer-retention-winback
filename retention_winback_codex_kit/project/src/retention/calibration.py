"""Sigmoid calibration fitted on a disjoint validation subset."""

import numpy as np
from sklearn.linear_model import LogisticRegression


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p)).reshape(-1, 1)


def fit_calibrator(p, y):
    return LogisticRegression(C=1e6, max_iter=1000).fit(logit(p), y)


def calibrate(model, p):
    return model.predict_proba(logit(p))[:, 1]
