"""Explicit hypothetical economics, prospective power, and dry-run assignments."""
import hashlib, math
import numpy as np
import pandas as pd
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
from .common import run_dir,save

def economics(p0=None,delta=None,V=None,m=None,D=None,r=None,c=None,count=0):
    inputs=[p0,delta,V,m,D,r,c]
    if any(x is None for x in inputs): return {'evidence_type':'NOT_AVAILABLE','value':None,'reason':'Enter all scenario assumptions'}
    if not all(np.isfinite(x) for x in inputs): raise ValueError('Inputs must be finite')
    p1=p0+delta
    if not all(0<=x<=1 for x in [p0,p1,m,r]) or min(V,D,c,count)<0: raise ValueError('Invalid probabilities or costs')
    value=delta*V*m-p1*r*D-c
    slope=V*m-r*D; threshold=(p0*r*D+c)/slope if slope>0 else None
    return {'evidence_type':'ASSUMPTION_SCENARIO','per_contact':value,'total':count*value,'break_even_delta':threshold,'break_even_feasible':threshold is not None and threshold<=1-p0,'assumptions':dict(zip(['p0','delta','V','m','D','r','c'],inputs))}

def power(p0,delta,alpha=.05,power_target=.8,comparisons=2,ratio=1):
    if not 0<p0<1 or not 0<p0+delta<1 or delta<=0 or not 0<alpha<1 or not 0<power_target<1 or comparisons<1 or ratio<=0: raise ValueError('Invalid planning assumptions')
    n=NormalIndPower().solve_power(effect_size=abs(proportion_effectsize(p0+delta,p0)),alpha=alpha/comparisons,power=power_target,ratio=ratio,alternative='two-sided')
    return {'evidence_type':'ASSUMPTION_SCENARIO','n_control':math.ceil(n),'n_treatment_each':math.ceil(n*ratio),'alpha_per_comparison':alpha/comparisons,'multiplicity':'Bonferroni planning','p0':p0,'delta':delta}

def assignments(ids,registry=None):
    registry={} if registry is None else registry.copy()
    for uid in ids:
        registry.setdefault(str(uid),['no_contact','reminder_content','incentive'][int(hashlib.sha256(('retention-experiment-v1:'+str(uid)).encode()).hexdigest()[:8],16)%3])
    return registry

def dry_run(mode):
    p=run_dir(mode); df=pd.read_parquet(p/'audiences/latest_unlabeled.parquet')
    from .common import read
    path=p/'audiences/assignment_registry.json'; registry=assignments(df.user_id,read(path) if path.exists() else None); save(path,registry)
    result=pd.DataFrame({'user_id':df.user_id,'arm':[registry[str(x)] for x in df.user_id],'status':'DRY_RUN_NOT_CONTACTABLE'})
    result.to_csv(p/'audiences/proposed_assignment.csv',index=False)
