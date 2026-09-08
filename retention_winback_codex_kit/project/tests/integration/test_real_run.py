"""Release assertions on real run outputs; never silently replace missing data."""
import os,json
import numpy as np
import pandas as pd
import joblib
from retention.common import ROOT,run_dir,read,connect,digest
from retention.features import FEATURES
from retention.modeling import predict,partition
from retention.cohorts import audience
MODE=os.environ.get('RETENTION_MODE','dev')

def test_source_and_conservation():
    q=read(run_dir(MODE)/'quality.json'); assert len(q['monthly_full_source'])==5 and q['coverage_usable']
    w=q['analytical_waterfall']; assert w['source_rows']==w['included']+w['excluded']
    source=read(ROOT/'data/manifests/acquisition.json')
    assert source['cosmetics']['status']=='acquired' and source['hillstrom']['rows']==64000
    assert all(len(f['sha256'])==64 for f in source['cosmetics']['files'])

def test_snapshot_labels_and_prediction_roundtrip():
    p=run_dir(MODE); freeze=read(p/'freeze.json'); model=joblib.load(p/'models'/f"{freeze['selected_model']}.joblib")
    for split in ['train','validation','test','latest_unlabeled']:
        x=pd.read_parquet(p/f'features_{split}.parquet'); y=pd.read_parquet(p/f'outcomes_{split}.parquet'); s=pd.read_parquet(p/f'scores_{split}.parquet')
        assert not x.user_id.duplicated().any(); assert (x.feature_max_timestamp<x.as_of_timestamp).all()
        assert (x.purchasing_days_60>=1).all(); assert 'non_repurchase_28d' not in s
        assert y.non_repurchase_28d.isna().all() if split=='latest_unlabeled' else y.non_repurchase_28d.notna().all()
        sample=s.head(100); np.testing.assert_allclose(predict(model,sample),sample.risk_probability,rtol=1e-10)
        exported=pd.read_parquet(p/'audiences'/f'{split}.parquet'); expected=audience(s,int(np.ceil(len(s)*.1)))
        assert exported.user_id.tolist()==expected.user_id.tolist(); assert exported.consent_status.eq('unknown').all()
        assert set(exported.user_id).isdisjoint(s.loc[s.suppression_reason.ne(''),'user_id'])
    assert pd.Timestamp('2019-12-01')+pd.Timedelta(days=28)<pd.Timestamp('2019-12-30')
    assert pd.Timestamp('2019-12-30')+pd.Timedelta(days=28)<pd.Timestamp('2020-01-28')

def test_trace_and_manifest_reconciliation():
    p=run_dir(MODE); index=read(p/'traces/index.json'); assert len(index)>0
    for row in index:
        events=pd.read_parquet(p/'traces'/f"{row['user_id']}.parquet")
        assert (events.event_time<pd.Timestamp('2020-01-28',tz='UTC')).all()
        assert events[['source_file','source_row']].duplicated().sum()==0
    manifest=read(p/'results_manifest.json')
    assert all(digest(p/f)==h for f,h in manifest['inputs_sha256'].items())
    for m in manifest['metrics']:
        assert {'dataset_id','run_mode','split','method','source_artifact','evidence_type','unit','denominator'}.issubset(m)
        assert m['dataset_id'] in ['rees46_cosmetics','hillstrom_email']
    tested=read(p/'test_metrics.json')
    for name,result in tested.items():
        m=next(x for x in manifest['metrics'] if x['metric_id']==name+'_brier'); assert m['value']==result['brier']

def test_hillstrom_separation():
    p=run_dir(MODE)/'hillstrom'; frozen=read(p/'freeze.json')
    assert not set(frozen['features'])&{'visit','conversion','spend','source_row_id','segment'}
    ids=[set(pd.read_csv(p/f'{s}_ids.csv').source_row_id) for s in ['train','validation','test']]
    assert ids[0].isdisjoint(ids[1]) and ids[1].isdisjoint(ids[2]) and ids[0].isdisjoint(ids[2])
    assert sum(x['n'] for x in read(p/'experiment.json')['arm_summary'])==64000
