"""Generate every reportable value from run artifacts with metric-level provenance."""
from pathlib import Path
import json,subprocess
import numpy as np
import pandas as pd
from .common import ROOT,run_dir,read,save,connect,DISCLOSURE,CUTS,digest,now
from .cohorts import audience

RECOMMENDATION='Use the frozen score as a candidate-ranking aid. Verify contactability and consent, then run a randomized holdout before claiming incremental purchases or benefit.'

def trace(mode='dev'):
    p=run_dir(mode); scores=pd.read_parquet(p/'scores_test.parquet'); diagnostic=pd.read_parquet(p/'test_diagnostics.parquet')
    records=diagnostic.merge(scores[['user_id','primary_segment','purchase_recency','purchasing_days_60']],on='user_id',validate='one_to_one')
    choices={'worked_example':records.sort_values('user_id').iloc[0]}
    for name,mask in [('false_positive',(records.risk_probability>=.5)&records.non_repurchase_28d.eq(0)),('false_negative',(records.risk_probability<.5)&records.non_repurchase_28d.eq(1))]:
        if mask.any(): choices[name]=records[mask].sort_values('user_id').iloc[0]
    for i,row in records.sort_values('user_id').iloc[1:13].iterrows(): choices[f'explorer_{row.user_id}']=row
    con=connect(mode,True); directory=p/'traces'; directory.mkdir(exist_ok=True); index=[]
    for kind,row in choices.items():
        uid=str(row.user_id); t=pd.Timestamp(CUTS['test'],tz='UTC')
        events=con.execute("SELECT source_file,source_row,event_time,event_type,product_id,category_id,price,valid_price,user_session,identical_row_count FROM int_behavior_events WHERE user_id=? AND event_time>=? AND event_time<? ORDER BY event_time,source_file,source_row",[uid,t-pd.Timedelta(days=60),t]).df()
        purchases=events[events.event_type.eq('purchase')]
        manual={'purchase_recency':(t-purchases.event_time.max()).total_seconds()/86400,'purchasing_days_60':int(purchases.event_time.dt.date.nunique()),'value_60':float(purchases.loc[purchases.valid_price,'price'].sum())}
        for key,value in manual.items(): np.testing.assert_allclose(value,row[key],rtol=1e-8)
        events.to_parquet(directory/f'{uid}.parquet',index=False)
        future=con.execute("SELECT source_file,source_row,event_time,event_type,price FROM int_behavior_events WHERE user_id=? AND event_time>=? AND event_time<? ORDER BY event_time,source_file,source_row",[uid,t,t+pd.Timedelta(days=28)]).df()
        assert int(not future.event_type.eq('purchase').any())==row.non_repurchase_28d
        future.to_parquet(directory/f'{uid}_retrospective.parquet',index=False)
        index.append({'kind':kind,'user_id':uid,'manual_reconciliation':manual,'risk':float(row.risk_probability),'segment':row.primary_segment,'retrospective_non_repurchase':int(row.non_repurchase_28d),'events':len(events)})
    con.close(); save(directory/'index.json',index)
    first=index[0]; (directory/'worked_customer.md').write_text(f"# One observed buyer, reconciled\n\n{DISCLOSURE}\n\nDataset: REES46 cosmetics. Run: {p.name}. Cutoff: 2020-01-28 UTC.\n\n{json.dumps(first,indent=2)}\n\nThe event file retains original filename and 1-based data-row position. Count distinct purchase dates, find the last purchase timestamp, and sum positive finite purchase prices to recover the three feature values. Identical rows remain present. The separate retrospective file covers [2020-01-28,2020-02-25).\n\nA false positive predicts non-repurchase but the customer returns. A false negative predicts repurchase but no purchase occurs within 28 days. Segment reasons describe observed history and do not identify causes.\n")
    return index

def reports(mode='dev'):
    p=run_dir(mode); quality=read(p/'quality.json'); freeze=read(p/'freeze.json'); tests=read(p/'test_metrics.json'); snapshots=read(p/'snapshots.json'); audiences=read(p/'audience_summary.json'); hill=read(p/'hillstrom/experiment.json'); uplift=read(p/'hillstrom/uplift.json')
    directory=p/'reports'; directory.mkdir(exist_ok=True); metrics=[]
    def add(key,value,unit='score',dataset='rees46_cosmetics',split='test',method='',source='',denominator=None,numerator=None,uncertainty=None,evidence='OBSERVED'):
        t=CUTS.get(split) if dataset=='rees46_cosmetics' else None
        metrics.append({'metric_id':key,'value':value,'unit':unit,'dataset_id':dataset,'run_id':p.name,'run_mode':mode if dataset=='rees46_cosmetics' else 'full_independent','as_of_timestamp':t,'window_start':t,'window_end_exclusive':str((pd.Timestamp(t)+pd.Timedelta(days=28)).date()) if t and split!='latest_unlabeled' else None,'split':split,'numerator':numerator,'denominator':denominator,'method':method,'uncertainty':uncertainty,'evidence_type':evidence,'source_artifact':source})
    for row in snapshots:
        add('eligible_buyers_'+row['split'],row['n'],'observed_customers',split=row['split'],method='At least one purchase in prior 60 days',source='snapshots.json')
        add('non_repurchase_prevalence_'+row['split'],row['non_repurchase_prevalence'],'fraction',split=row['split'],denominator=row['n'] if row['label_mature'] else None,method='Mean mature 28-day non-repurchase',source='snapshots.json',evidence='OBSERVED' if row['label_mature'] else 'NOT_AVAILABLE')
    for model,result in tests.items():
        for key in ['roc_auc','average_precision_non_repurchase','average_precision_repurchase','brier','log_loss']:
            add(f'{model}_{key}',result[key],method=f'Frozen {model}; sklearn {key}',source='test_metrics.json',denominator=result['n'],uncertainty=result['uncertainty']['intervals'].get(key))
        for row in result['top_k']:
            add(f'{model}_lift_top_{int(row["fraction"]*100)}pct',row['risk_ranking_lift'],'ratio',method='Top-K precision / same-cohort prevalence; deterministic ID tie break',source='test_metrics.json',denominator=row['k'],numerator=row['positive_count'])
    for row in audiences: add('candidate_count_'+row['split'],row['selected'],'observed_customers',split=row['split'],method='Frozen capacity, exclusions and risk ranking; consent unknown',source='audience_summary.json',denominator=row['eligible'])
    for arm in hill['arm_summary']:
        for key in ['visit_rate','conversion_rate','mean_spend_per_assigned']:
            add('hillstrom_'+arm['arm']+'_'+key,arm[key],unit='dollars_per_assigned' if key.startswith('mean') else 'fraction',dataset='hillstrom_email',split='randomized_all',denominator=arm['n'],method='Assigned-customer mean, 14-day outcome',source='hillstrom/experiment.json')
    for row in hill['effects']: add('hillstrom_'+row['arm']+'_'+row['outcome']+'_difference',row['difference'],unit='absolute_difference',dataset='hillstrom_email',split='randomized_all',method=hill['interval_method'],source='hillstrom/experiment.json',uncertainty=row['ci95_unadjusted'])
    add('hillstrom_visit_qini',uplift['qini_auc'],dataset='hillstrom_email',split='test',method='sklift.metrics.qini_auc_score, fixed T-learner visit rankings',source='hillstrom/uplift.json',uncertainty=uplift['qini_ci95'])
    add('source_rows',sum(x['n'] for x in quality['monthly_full_source']),'source_events',split='source_coverage',method='Count every row in original five archives, before dev sampling',source='quality.json')
    manifest={'generated_at':now(),'dataset_separation':'never joined','disclosure':DISCLOSURE,'selected_model':freeze['selected_model'],'recommendation':RECOMMENDATION,'metrics':metrics,'inputs_sha256':{f:digest(p/f) for f in ['quality.json','freeze.json','test_metrics.json','snapshots.json','audience_summary.json','hillstrom/experiment.json','hillstrom/uplift.json']}}
    save(p/'results_manifest.json',manifest)
    table=pd.DataFrame([{k:r[k] for k in ['metric_id','value','dataset_id','split','unit']} for r in metrics])
    table.to_csv(directory/'metrics.csv',index=False)
    comparison=pd.DataFrame([{ 'model':name,**{k:r[k] for k in ['n','roc_auc','average_precision_non_repurchase','average_precision_repurchase','brier','log_loss']}} for name,r in tests.items()])
    comparison.to_csv(directory/'model_comparison.csv',index=False)
    chosen=tests[freeze['selected_model']]
    text=f"# Analytical report\n\n{DISCLOSURE}\n\nRun {p.name}. Source coverage October 2019 through February 2020. All reported numbers load from results_manifest.json.\n\n## Decision\n\n{RECOMMENDATION}\n\nValidation selected {freeze['selected_model']} by Brier score before test inspection. Test ROC-AUC {chosen['roc_auc']:.4f}, Brier {chosen['brier']:.4f}, non-repurchase prevalence {chosen['non_repurchase_prevalence']:.2%}.\n\n## Out-of-time comparisons\n\n{comparison.to_markdown(index=False)}\n\nThe ablation compares purchase-only and combined models on exactly the same snapshots. Average precision for non-repurchase must be compared with the high non-repurchase prevalence. Ranking lift measures concentration of future non-repurchase, not response to contact.\n\n## Data quality\n\n{json.dumps(quality['analytical_waterfall'],indent=2)}\n\nSource multiplicity is preserved. Inferred purchase occasions group user and timestamp. Price totals are historical event-value proxies in unverified source monetary units. Missing prices do not remove behavioral purchases. Cart removals are not refunds. Daily presence supports the observation windows but cannot rule out intraday outages.\n\n## Limitations\n\nThe same observed user may appear at successive cutoffs. IDs never enter predictors. First purchase age is first observed within the 60-day window, not customer tenure. Provided session keys are customer scoped and missingness is explicit; no sessions or product metadata are backfilled. Only five historical months are available. Neither consent nor contactability is known. No cosmetics campaign has run.\n\n## Independent Hillstrom experiment\n\n{pd.DataFrame(hill['arm_summary']).to_markdown(index=False)}\n\nQini on untouched visit test partition: {uplift['qini_auc']:.5f}, 95% interval {uplift['qini_ci95']}. Heterogeneous targeting may be noisy even when average treatment effects exist. The campaign labels name merchandise creatives, not customer gender.\n\n## Artifact provenance\n\nSee results_manifest.json for every metric's dataset, window, split, method and source artifact. See traces/ for source-row reconciliations and separate retrospective outcomes.\n"
    (directory/'analytical_report.md').write_text(text)
    (directory/'executive_memo.md').write_text(f"# Executive decision memo\n\n{DISCLOSURE}\n\n{RECOMMENDATION}\n\n{freeze['selected_model']} was selected before the test. Test Brier = {chosen['brier']:.4f}; constant baseline = {tests['constant']['brier']:.4f}. Latest analytical candidates = {audiences[-1]['selected']:,}. These are proposed audiences with unknown consent.\n\nThe next investment is verified customer identity, contact permission, campaign delivery, cost and margin data, followed by a prospective experiment. Historical risk is insufficient to forecast incremental benefit. The independent Hillstrom readout teaches randomized measurement and does not estimate this retailer's campaign effect.\n")
    (directory/'hillstrom_readout.md').write_text('# Hillstrom randomized email experiment — independent dataset\n\n'+pd.DataFrame(hill['effects']).to_markdown(index=False)+'\n\n'+pd.DataFrame(uplift['policies']).T.to_markdown()+'\n\nAll denominators include assigned nonconverters. Conversion is primary; visits and spend are secondary. Creative names do not identify gender. Qini uncertainty and support must guide any claim about ranking improvement.\n')
    # Equal capacity retrospective comparison, labels only in this diagnostic artifact.
    scores=pd.read_parquet(p/'scores_test.parquet'); outcomes=pd.read_parquet(p/'outcomes_test.parquet'); policies=[]
    for name in ['recency','risk','value','risk_value']:
        selected=audience(scores,int(np.ceil(len(scores)*.1)),name).merge(outcomes[['user_id','non_repurchase_28d']],on='user_id',validate='one_to_one')
        policies.append({'policy':name,'k':len(selected),'non_repurchase_rate':float(selected.non_repurchase_28d.mean()),'mean_historical_value_proxy':float(selected.historical_value_proxy.mean())})
    pd.DataFrame(policies).to_csv(directory/'policy_comparison.csv',index=False)
    bi=p/'bi'; bi.mkdir(exist_ok=True)
    for split in CUTS:
        pd.read_parquet(p/f'scores_{split}.parquet').to_parquet(bi/f'customer_scores_{split}.parquet',index=False)
    table.to_csv(bi/'metrics.csv',index=False)
    return manifest

def presentation(mode='dev'):
    subprocess.run(['node',str(ROOT/'scripts/build_slides.mjs'),mode],check=True)
