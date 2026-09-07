"""Tiny artificial fixtures exclusively for correctness tests, never analytical results."""
import duckdb
import numpy as np
import pandas as pd
import pytest
from retention.snapshots import snapshot_sql
from retention.features import validate_features
from retention.modeling import partition
from retention.evaluation import top_indices
from retention.experiments import economics,power,assignments
from retention.cohorts import segment,audience

def test_cutoff_purchase_presence_and_inactive_buyer():
    c=duckdb.connect(); c.execute("SET TimeZone='UTC'")
    c.execute('CREATE TABLE int_behavior_events(user_id VARCHAR,event_time TIMESTAMPTZ,event_type VARCHAR,price DOUBLE,valid_price BOOLEAN,user_session VARCHAR,product_id VARCHAR,category_id VARCHAR)')
    rows=[('a','2019-11-01','purchase',None,False,'s','p','9000000000000000001'),('a','2019-12-01','purchase',10,True,'s','p','future'),('b','2019-11-05','purchase',5,True,None,'p',None),('b','2019-12-29','purchase',5,True,'s','p',None)]
    c.executemany('INSERT INTO int_behavior_events VALUES(?,?,?,?,?,?,?,?)',rows)
    df=c.execute(snapshot_sql('2019-12-01')).df().set_index('user_id')
    assert set(df.index)=={'a','b'}
    assert df.loc['a','purchasing_days_60']==1 and df.loc['a','value_60']==0
    assert df.loc['a','purchase_categories']==1
    assert df.loc['b','active_days_14']==0
    assert df.loc['a','purchase_recency']==30
    assert c.execute("SELECT count(*) FROM int_behavior_events WHERE user_id='a' AND event_time>='2019-12-01' AND event_time<'2019-12-29'").fetchone()[0]==1
    assert c.execute("SELECT count(*) FROM int_behavior_events WHERE user_id='b' AND event_time>='2019-12-01' AND event_time<'2019-12-29'").fetchone()[0]==0
    c.close()

def test_allowlist_partition_and_ties():
    for col in ['user_id','non_repurchase_28d','next_purchase_date','visit']:
        with pytest.raises(ValueError): validate_features([col])
    ids=np.array([str(i) for i in range(100)])
    mask=partition(ids); assert 0<mask.sum()<100
    assert set(ids[mask]).isdisjoint(ids[~mask])
    assert top_indices([.5,.5],['b','a'],.5).tolist()==[1]
    assert len(top_indices([],[],.1))==0

def test_economics_and_assignment():
    assert economics()['value'] is None
    assert economics(.1,.01,100,.3,5,1,0,count=100)['per_contact']==pytest.approx(-.25)
    with pytest.raises(ValueError): economics(.99,.1,100,.3,5,1,0)
    assert not economics(.1,.01,1,.1,5,1,0)['break_even_feasible']
    assert power(.1,.01)['n_control']>100
    a=assignments(['a','b']); assert assignments(['c','a'],a)['a']==a['a']

def test_segment_precedence_and_audience():
    df=pd.DataFrame({'user_id':['a','b'],'purchase_recency':[1,30],'valid_price_share':[1,1],'value_60':[100,10],'activity_change':[-5,0],'views_28':[5,0],'carts_28':[0,0],'repeat_buyer':[True,False],'event_recency':[1,30]})
    result=segment(df,50)
    assert result.primary_segment.tolist()==['recent_purchase_suppressed','observed_one_time']
    for col in ['dataset_id','run_id','as_of_date','model_version','feature_contract_version','risk_rank']: result[col]='test_fixture'
    result['historical_value_proxy']=result.value_60; result['risk_probability']=.8; result['risk_value_priority']=1
    result['contactability_status']='unknown'; result['consent_status']='unknown'
    assert len(audience(result,0))==0
    assert audience(result,100).user_id.tolist()==['b']
    assert 'non_repurchase_28d' not in audience(result,100)
