"""Ranking and calibration metrics on mature, single-snapshot customers."""
import math
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss,confusion_matrix

def top_indices(probability, ids, fraction):
    if not 0<=fraction<=1: raise ValueError('fraction outside [0,1]')
    n=len(ids); k=min(n,math.ceil(n*fraction))
    return np.lexsort((np.asarray(ids,dtype=str),-np.asarray(probability)))[:k]

def metrics(y,p,ids,threshold=.5):
    y=np.asarray(y,dtype=int); p=np.asarray(p); n=len(y)
    if not n: raise ValueError('No mature evaluation rows')
    prevalence=float(y.mean())
    result={'n':n,'non_repurchase_prevalence':prevalence,'repurchase_prevalence':1-prevalence,
    'roc_auc':float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,
    'average_precision_non_repurchase':float(average_precision_score(y,p)),
    'average_precision_repurchase':float(average_precision_score(1-y,1-p)),
    'brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,p,labels=[0,1])),
    'threshold':threshold,'confusion_matrix':confusion_matrix(y,p>=threshold,labels=[0,1]).tolist()}
    result['top_k']=[]
    for f in [.05,.1,.2]:
        ix=top_indices(p,ids,f); positives=int(y[ix].sum()); k=len(ix)
        result['top_k'].append({'fraction':f,'k':k,'positive_count':positives,'precision':positives/k,'recall_capture':positives/int(y.sum()) if y.sum() else None,'risk_ranking_lift':positives/k/prevalence if prevalence else None})
    bins=np.minimum((p*10).astype(int),9)
    result['reliability']=[{'bin':int(b),'n':int((bins==b).sum()),'predicted':float(p[bins==b].mean()),'observed':float(y[bins==b].mean())} for b in np.unique(bins)]
    return result

def bootstrap(y,p,ids,reps=200):
    rng=np.random.default_rng(2801); y=np.asarray(y); p=np.asarray(p); ids=np.asarray(ids)
    vals=[]
    for _ in range(reps):
        ix=rng.integers(0,len(y),len(y)); yy=y[ix]; pp=p[ix]
        if len(np.unique(yy))<2: continue
        k=top_indices(pp,ids[ix],.1)
        vals.append([roc_auc_score(yy,pp),brier_score_loss(yy,pp),yy[k].mean()/yy.mean()])
    return {'method':'200 customer bootstrap resamples; percentile 95% CI; one row/customer; fixed model','intervals':{name:np.quantile(np.asarray(vals)[:,i],[.025,.975]).tolist() for i,name in enumerate(['roc_auc','brier','lift_top_10pct'])}}
