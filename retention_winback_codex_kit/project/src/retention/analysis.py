"""Supplemental quality, training-only EDA, and explanatory diagnostics."""
import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from threadpoolctl import threadpool_limits
from .common import run_dir,connect,save,read
from .features import FEATURES
from .modeling import load_split,partition,predict

def supplement(mode):
    p=run_dir(mode); con=connect(mode,True)
    q={}
    q['event_quality']=con.execute("SELECT source_file,event_type,count(*) n,count(*) FILTER(WHERE NOT valid_behavior) excluded,count(*) FILTER(WHERE NOT valid_price) invalid_price,count(*) FILTER(WHERE user_session IS NULL) missing_session,count(*) FILTER(WHERE category_id IS NULL) missing_category,count(*) FILTER(WHERE brand IS NULL) missing_brand FROM stg_cosmetics_events GROUP BY 1,2 ORDER BY 1,2").df().to_dict('records')
    q['sessions_shared_by_users']=con.execute("SELECT count(*) FROM (SELECT user_session FROM int_behavior_events WHERE user_session IS NOT NULL GROUP BY 1 HAVING count(DISTINCT user_id)>1)").fetchone()[0]
    q['most_active_ids_local_only']=con.execute('SELECT user_id,count(*) n FROM int_behavior_events GROUP BY 1 ORDER BY n DESC LIMIT 10').df().to_dict('records')
    q['source_schema']=con.execute('DESCRIBE source_events').df().to_dict('records')
    save(p/'quality_detail.json',q)
    # Purchase-gap survival uses first observed purchase with administrative censoring before training origin.
    gaps=con.execute("""WITH purchases AS (SELECT DISTINCT user_id,event_time FROM int_behavior_events WHERE event_type='purchase' AND event_time<'2019-12-01'), ordered AS (SELECT user_id,event_time,row_number() OVER(PARTITION BY user_id ORDER BY event_time) rn FROM purchases)
    SELECT user_id,min(event_time) first_purchase,max(event_time) FILTER(WHERE rn=2) second_purchase,
    epoch(coalesce(max(event_time) FILTER(WHERE rn=2),TIMESTAMPTZ '2019-12-01')-min(event_time))/86400 duration_days,
    count(*) FILTER(WHERE rn=2)>0 returned FROM ordered GROUP BY user_id""").df()
    # Daily Kaplan-Meier table, keeping censored buyers in risk sets.
    survival=1.; curve=[]
    for day in range(61):
        at_risk=int((gaps.duration_days>=day).sum()); deaths=int(((gaps.duration_days>=day)&(gaps.duration_days<day+1)&gaps.returned).sum())
        if at_risk: survival*=1-deaths/at_risk
        curve.append({'day':day,'at_risk':at_risk,'observed_second_purchases':deaths,'estimated_no_second_purchase':survival})
    pd.DataFrame(curve).to_csv(p/'reports/purchase_gap_survival.csv',index=False)
    train=load_split(mode,'train')
    train.assign(activity_declined=train.activity_change<0).groupby(['repeat_buyer','activity_declined']).agg(n=('user_id','size'),non_repurchase_rate=('non_repurchase_28d','mean'),value_proxy=('value_60','median')).reset_index().to_csv(p/'reports/training_eda.csv',index=False)
    val=load_split(mode,'validation'); policy=val[~partition(val.user_id)]
    frozen=read(p/'freeze.json'); model=joblib.load(p/'models'/f"{frozen['selected_model']}.joblib")
    with threadpool_limits(limits=2):
        importance=permutation_importance(model['estimator'],policy[model['features']],policy.non_repurchase_28d.astype(int),scoring='neg_brier_score',n_repeats=3,random_state=2801,n_jobs=1)
    pd.DataFrame({'feature':model['features'],'importance_mean':importance.importances_mean,'importance_std':importance.importances_std}).sort_values('importance_mean',ascending=False).to_csv(p/'reports/permutation_importance.csv',index=False)
    log=joblib.load(p/'models/logistic_combined.joblib')
    pd.DataFrame({'feature':log['features'],'standardized_coefficient':log['estimator'][-1].coef_[0]}).to_csv(p/'reports/logistic_coefficients.csv',index=False)
    diagnostics=pd.read_parquet(p/'test_diagnostics.parquet'); cut=float(train.value_60.quantile(.75))
    bands=diagnostics.assign(value_band=np.where(diagnostics.value_60>=cut,'training_top_quartile','lower_value')).groupby('value_band').agg(n=('user_id','size'),observed_non_repurchase=('non_repurchase_28d','mean'),mean_risk=('risk_probability','mean')).reset_index()
    bands['observed_rate_ci_halfwidth']=1.96*np.sqrt(bands.observed_non_repurchase*(1-bands.observed_non_repurchase)/bands.n)
    bands.to_csv(p/'reports/value_band_metrics.csv',index=False)
    con.close()
