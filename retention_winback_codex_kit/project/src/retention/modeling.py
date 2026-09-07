"""Fixed candidates; fit train only, calibrate and select on disjoint validation users."""
import hashlib
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.inspection import permutation_importance
from threadpoolctl import threadpool_limits
from .common import run_dir,save,read,now,digest,CUTS
from .features import PURCHASE,FEATURES,validate_features
from .calibration import fit_calibrator,calibrate
from .evaluation import metrics,bootstrap

def load_split(mode,split):
    p=run_dir(mode)
    x=pd.read_parquet(p/f'features_{split}.parquet')
    y=pd.read_parquet(p/f'outcomes_{split}.parquet')
    df=x.merge(y[['user_id','non_repurchase_28d','label_mature']],on='user_id',validate='one_to_one')
    if not df.label_mature.all() or df.non_repurchase_28d.isna().any(): raise ValueError('Immature labels cannot be supervised')
    return df

def partition(ids):
    # Separate salted digest avoids correlation with the dev sampling bucket.
    return np.array([int(hashlib.md5(('calibration:'+str(x)).encode()).hexdigest()[:8],16)%2==0 for x in ids])

def predict(bundle,df,calibrated=True):
    features=bundle['features']; validate_features(features)
    with threadpool_limits(limits=2): p=bundle['estimator'].predict_proba(df[features])[:,1]
    return calibrate(bundle['calibrator'],p) if calibrated and bundle['calibrator'] is not None else p

def train(mode='dev'):
    p=run_dir(mode)
    if (p/'test_evaluated.json').exists(): raise RuntimeError('Run already unblinded; use saved model. A redesign needs a new run version and disclosure.')
    train=load_split(mode,'train'); val=load_split(mode,'validation'); mask=partition(val.user_id)
    assert set(val.loc[mask,'user_id']).isdisjoint(set(val.loc[~mask,'user_id']))
    if min(mask.sum(),(~mask).sum())<30: raise ValueError('Insufficient calibration/policy sample')
    specs=[('constant',FEATURES,DummyClassifier(strategy='prior')),('recency',['purchase_recency'],LogisticRegression(C=1,max_iter=1000)),('logistic_purchase',PURCHASE,LogisticRegression(C=1,max_iter=1000)),('logistic_combined',FEATURES,LogisticRegression(C=1,max_iter=1000)),('tree_purchase',PURCHASE,HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=15,min_samples_leaf=50,l2_regularization=1,random_state=2801)),('tree_combined',FEATURES,HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=15,min_samples_leaf=50,l2_regularization=1,random_state=2801))]
    results={}; bundles={}; (p/'models').mkdir(exist_ok=True)
    for name,features,estimator in specs:
        validate_features(features)
        model=make_pipeline(SimpleImputer(strategy='median',keep_empty_features=True),StandardScaler(),estimator)
        with threadpool_limits(limits=2): model.fit(train[features],train.non_repurchase_28d.astype(int))
        bundle={'estimator':model,'features':features,'calibrator':None,'name':name,'mode':mode,'feature_contract_version':'1.0'}
        if name!='constant': bundle['calibrator']=fit_calibrator(predict(bundle,val[mask]),val.loc[mask,'non_repurchase_28d'].astype(int))
        results[name]={'uncalibrated':metrics(val.loc[~mask,'non_repurchase_28d'],predict(bundle,val[~mask],False),val.loc[~mask,'user_id']), 'calibrated':metrics(val.loc[~mask,'non_repurchase_28d'],predict(bundle,val[~mask]),val.loc[~mask,'user_id'])}
        joblib.dump(bundle,p/'models'/f'{name}.joblib'); bundles[name]=bundle
        print(name,results[name]['calibrated']['brier'],flush=True)
    selected=min(results,key=lambda k:results[k]['calibrated']['brier'])
    frozen={'time':now(),'selected_model':selected,'selection':'minimum Brier on validation-policy customers','calibration_n':int(mask.sum()),'policy_n':int((~mask).sum()),'threshold':.5,'capacity_fraction':.1,'recent_suppression_days':7,'high_value_threshold':float(train.value_60.quantile(.75)),'feature_contract_version':'1.0','cuts':CUTS,'mode':mode,'model_hashes':{name:digest(p/'models'/f'{name}.joblib') for name in bundles},'feature_allowlist':FEATURES}
    save(p/'validation_metrics.json',results); save(p/'freeze.json',frozen)
    for name,bundle in bundles.items():
        np.testing.assert_allclose(predict(bundle,val.head(50)),predict(joblib.load(p/'models'/f'{name}.joblib'),val.head(50)),rtol=1e-12)
    return frozen

def evaluate(mode='dev'):
    p=run_dir(mode); freeze=read(p/'freeze.json'); test=load_split(mode,'test'); result={}
    for name,h in freeze['model_hashes'].items():
        if digest(p/'models'/f'{name}.joblib')!=h: raise ValueError('Frozen model hash mismatch')
        bundle=joblib.load(p/'models'/f'{name}.joblib'); prediction=predict(bundle,test)
        result[name]=metrics(test.non_repurchase_28d,prediction,test.user_id)
        result[name]['uncertainty']=bootstrap(test.non_repurchase_28d,prediction,test.user_id)
        if name==freeze['selected_model']:
            diagnostic=test[['user_id','as_of_timestamp','non_repurchase_28d','repeat_buyer','value_60']].copy(); diagnostic['risk_probability']=prediction
            diagnostic.to_parquet(p/'test_diagnostics.parquet',index=False)
            groups=[]
            for repeat,group in diagnostic.groupby('repeat_buyer'):
                groups.append({'group':f'repeat_buyer={repeat}',**metrics(group.non_repurchase_28d,group.risk_probability,group.user_id)})
            save(p/'subgroup_metrics.json',groups)
    save(p/'test_metrics.json',result); save(p/'test_evaluated.json',{'time':now(),'freeze_sha256':digest(p/'freeze.json'),'post_test_design_changes':False})
    return result
